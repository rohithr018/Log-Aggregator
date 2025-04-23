import { useState } from 'react'
import viteLogo from '/vite.svg'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="text-center p-8">
      <div className="flex justify-center gap-8 mb-8">
        <a href="https://vite.dev" target="_blank">
          <img src={viteLogo} className="logo w-20" alt="Vite logo" />
        </a>
      </div>
      <h1 className="text-4xl font-semibold mb-4">Vite + React</h1>
      <div className="card max-w-sm mx-auto p-4 bg-gray-800 text-white rounded-lg shadow-lg">
        <button
          onClick={() => setCount((count) => count + 1)}
          className="bg-blue-500 text-white p-2 rounded-lg hover:bg-blue-700 transition"
        >
          count is {count}
        </button>
        <p className="mt-4 text-gray-400">
          Edit <code className="text-blue-400">src/App.jsx</code> and save to test HMR
        </p>
      </div>
      <p className="read-the-docs mt-4 text-gray-400">
        Click on the Vite and React logos to learn more
      </p>
    </div>
  )
}

export default App
