import { useEffect, useState } from 'react'
import { SignedIn, SignedOut, useUser } from '@clerk/nextjs'
import axios from 'axios'
import NavBar from '../components/NavBar'
import PortfolioCard from '../components/PortfolioCard'
import PortfolioChart from '../components/PortfolioChart'

export default function Dashboard() {
  const [data, setData] = useState(null)
  const { isLoaded, user } = useUser()

  useEffect(() => {
    async function fetchDashboard() {
      try {
        const res = await axios.get(`${process.env.NEXT_PUBLIC_API_BASE}/api/dashboard`, { withCredentials: true })
        setData(res.data)
      } catch (err) {
        console.error(err)
      }
    }
    fetchDashboard()
  }, [])

  return (
    <div className="min-h-screen bg-gray-50">
      <NavBar />
      <main className="max-w-6xl mx-auto p-6">
        <SignedOut>
          <div className="text-center p-8 bg-white rounded shadow">Please sign in to see your dashboard.</div>
        </SignedOut>

        <SignedIn>
          <h2 className="text-2xl font-semibold mb-4">Welcome{user ? `, ${user.firstName || ''}` : ''}</h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <PortfolioCard title="Total Value" value={data ? `$${data.totalValue}` : '–'} />
            <PortfolioCard title="Open Orders" value={data ? data.openOrders : '–'} />
            <PortfolioCard title="Profit / Loss" value={data ? `$${data.profitLoss}` : '–'} />
          </div>

          <div className="bg-white p-4 rounded shadow">
            <h3 className="font-medium mb-2">Portfolio Trend</h3>
            <PortfolioChart points={data ? data.trend : [100,110,120,115,130]} />
          </div>
        </SignedIn>
      </main>
    </div>
  )
}

