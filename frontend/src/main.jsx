import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'

// Pega a div 'root' do index.html e renderiza o componente App dentro dela
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)