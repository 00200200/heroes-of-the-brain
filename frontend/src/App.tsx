import { useEffect, useState } from 'react'
import HomePage from './pages/HomePage'
import StressPage from './pages/StressPage'
import PomodoroPage from './pages/PomodoroPage'
import './App.css'
import Layout from './components/Layout/Layout';
import { Home } from 'lucide-react';

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
      {currentPage === 'home' && <HomePage></HomePage>}
      {currentPage === 'stress' && <StressPage></StressPage>}
      {currentPage === 'pomodoro' && <PomodoroPage></PomodoroPage>}  
    </Layout>
  );

}

export default App;
