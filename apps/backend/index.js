require('dotenv').config()
const express = require('express')
const bodyParser = require('body-parser')
const cors = require('cors')
const { Pool } = require('pg')

const app = express()
app.use(cors({ origin: 'http://localhost:3000', credentials: true }))
app.use(bodyParser.json())

// Database connection configuration
if (!process.env.DATABASE_URL) {
  console.error('❌ ERROR: DATABASE_URL is not set in .env file')
  console.error('Please add DATABASE_URL to your .env file')
  process.exit(1)
}

// Configure SSL for cloud databases (Neon, Supabase, Railway, etc.)
const getSSLConfig = () => {
  const dbUrl = process.env.DATABASE_URL || ''
  
  // Cloud providers that typically require SSL
  const cloudProviders = ['neon.tech', 'supabase.co', 'railway.app', 'render.com', 'heroku.com']
  const isCloudDB = cloudProviders.some(provider => dbUrl.includes(provider))
  
  if (isCloudDB || dbUrl.includes('sslmode=require')) {
    return { rejectUnauthorized: false }
  }
  
  return false
}

const pool = new Pool({ 
  connectionString: process.env.DATABASE_URL,
  ssl: getSSLConfig()
})

// Test database connection
async function testDatabaseConnection() {
  try {
    console.log('🔄 Attempting to connect to PostgreSQL database...')
    const client = await pool.connect()
    const result = await client.query('SELECT NOW(), version()')
    client.release()
    
    console.log('✅ Successfully connected to PostgreSQL database!')
    console.log('📊 Database time:', result.rows[0].now)
    console.log('🔧 PostgreSQL version:', result.rows[0].version.split(' ')[0] + ' ' + result.rows[0].version.split(' ')[1])
    
    // Test if tables exist
    const tablesResult = await pool.query(`
      SELECT table_name 
      FROM information_schema.tables 
      WHERE table_schema = 'public'
      ORDER BY table_name
    `)
    
    if (tablesResult.rows.length > 0) {
      console.log('📋 Found tables:', tablesResult.rows.map(r => r.table_name).join(', '))
    } else {
      console.log('⚠️  No tables found. Make sure you have run db/schema.sql')
    }
    
    return true
  } catch (err) {
    console.error('❌ Failed to connect to database:')
    console.error('Error:', err.message)
    if (err.code === 'ECONNREFUSED') {
      console.error('💡 Tip: Make sure PostgreSQL is running and DATABASE_URL is correct')
    } else if (err.code === '28P01') {
      console.error('💡 Tip: Check your database username and password')
    } else if (err.code === '3D000') {
      console.error('💡 Tip: The database does not exist. Create it first.')
    }
    return false
  }
}

// Simple health check with database status
app.get('/api/health', async (req, res) => {
  try {
    await pool.query('SELECT 1')
    res.json({ ok: true, database: 'connected' })
  } catch (err) {
    res.json({ ok: false, database: 'disconnected', error: err.message })
  }
})

// Sample protected route (in production validate user via Clerk)
app.get('/api/dashboard', async (req, res) => {
  try {
    // TODO: verify session with Clerk (server-side) before returning user data
    // For now, return sample aggregated values
    const totalValueResult = await pool.query('SELECT COALESCE(SUM(current_value),0) AS total FROM holdings WHERE owner_id = $1', ['demo-user'])
    const totalValue = totalValueResult.rows[0].total || 0

    // Dummy trend data - replace with real historic values query
    const trend = [100, 110, 120, 115, 130]

    res.json({ totalValue, trend, openOrders: 2, profitLoss: 350 })
  } catch (err) {
    console.error(err)
    res.status(500).json({ error: 'server error' })
  }
})

// GET wines
app.get('/api/wines', async (req, res) => {
  try {
    const r = await pool.query('SELECT * FROM wines LIMIT 100')
    res.json(r.rows)
  } catch (err) { res.status(500).json({ error: String(err) }) }
})

// POST create holding
app.post('/api/holdings', async (req, res) => {
  const { owner_id, wine_id, qty, purchase_price } = req.body
  try {
    const r = await pool.query('INSERT INTO holdings(owner_id, wine_id, qty, purchase_price, current_value) VALUES($1,$2,$3,$4,$4) RETURNING *', [owner_id, wine_id, qty, purchase_price])
    res.json(r.rows[0])
  } catch (err) { res.status(500).json({ error: String(err) }) }
})

// Start server after database connection is verified
const port = process.env.PORT || 4000

async function startServer() {
  const dbConnected = await testDatabaseConnection()
  
  if (!dbConnected) {
    console.error('\n❌ Cannot start server without database connection.')
    console.error('Please fix the database connection and try again.\n')
    process.exit(1)
  }
  
  app.listen(port, () => {
    console.log('\n🚀 Server is running!')
    console.log(`📍 Backend API: http://localhost:${port}`)
    console.log(`🔗 Health check: http://localhost:${port}/api/health`)
    console.log(`📡 Frontend should connect to: http://localhost:${port}\n`)
  })
}

// Handle graceful shutdown
process.on('SIGINT', async () => {
  console.log('\n🛑 Shutting down gracefully...')
  await pool.end()
  console.log('✅ Database connections closed')
  process.exit(0)
})

process.on('SIGTERM', async () => {
  console.log('\n🛑 Shutting down gracefully...')
  await pool.end()
  console.log('✅ Database connections closed')
  process.exit(0)
})

// Start the server
startServer().catch(err => {
  console.error('❌ Failed to start server:', err)
  process.exit(1)
})

