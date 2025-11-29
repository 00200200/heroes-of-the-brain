import { useEffect, useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
//TODO Pomodoro Page --- Stress Page --- below
//import HomePage from './pages/HomePage'
//import PomodoroPage from './pages/PomodoroPage'
import './App.css'
import Layout from './components/Layout/Layout';

function App() {
  const [currentPage, setCurrentPage] = useState(
		window.location.hash === '#/pomodoro' ? 'pomodoro' :
		window.location.hash === '#/stress' ? 'stress' :
		'home'
	);

  useEffect(() => {
    const handleHashChange = () => {
			const hash = window.location.hash;
			if (hash === '#/pomodoro') {
				setCurrentPage('pomodoro');
			} else if (hash === '#/stress') {
				setCurrentPage('stress');
			} else {
				setCurrentPage('home');
			}
		};

    window.addEventListener('hashchange', handleHashChange);
		return () => window.removeEventListener('hashchange', handleHashChange);

  }, []);
  
  return (
    // temporary layout structure
    <Layout> 
      {currentPage === 'home' && <div>Home Page Component</div>}
      {currentPage === 'pomodoro' && <div>Pomodoro Page Component</div>}
      {currentPage === 'stress' && <div>Stress Page Component</div>}  
    </Layout>
  );

}

export default App;
