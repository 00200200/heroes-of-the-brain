import { useEffect, useState } from 'react'
import HomePage from './pages/HomePage'
import StressPage from './pages/StressPage'
import PomodoroPage from './pages/PomodoroPage'
import ConcentrationPage from './pages/ConcentrationPage'
import './App.css'
import Layout from './components/Layout/Layout';
import { Home } from 'lucide-react';
import MusicPlayer from './components/context/MusicPlayer'
import { MusicProvider } from './components/context/MusicContext'

function App() {
  const [currentPage, setCurrentPage] = useState(
		window.location.hash === '#/pomodoro' ? 'pomodoro' :
		window.location.hash === '#/stress' ? 'stress' :
    window.location.hash === '#/concentration' ? 'concentration' :
		'home'
	);

  useEffect(() => {
    const handleHashChange = () => {
			const hash = window.location.hash;
			if (hash === '#/pomodoro') {
				setCurrentPage('pomodoro');
			} else if (hash === '#/stress') {
				setCurrentPage('stress');
			} else if (hash === '#/concentration')
        setCurrentPage('concentration')
      else {
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
      {currentPage === 'concentration' && <ConcentrationPage></ConcentrationPage>} 
      <MusicProvider>
      <MusicPlayer />
      </MusicProvider>
    </Layout>
  );

}

export default App;
