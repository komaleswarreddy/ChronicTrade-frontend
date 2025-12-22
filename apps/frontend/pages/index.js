import Head from 'next/head'
import NavBar from '../components/NavBar'

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-wine-50 to-white">
      <Head>
        <title>Wine Invest — Welcome</title>
      </Head>
      <NavBar />
      <main className="max-w-4xl mx-auto p-6">
        <section className="mt-12 bg-white p-8 rounded shadow">
          <h2 className="text-xl font-semibold">Start your wine portfolio</h2>
          <p className="mt-2 text-gray-600">Sign in to view your holdings, predictions, and arbitrage alerts.</p>
        </section>
      </main>
    </div>
  )
}

