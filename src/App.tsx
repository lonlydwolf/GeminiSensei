import { useApp } from './hooks/useApp';
import { AppRoute } from './types';
import Layout from './components/Layout';
import Welcome from './pages/Welcome';
import Home from './pages/Home';
import Roadmap from './pages/Roadmap';
import Chat from './pages/Chat';
import Settings from './pages/Settings';
import { Loader2, AlertCircle } from 'lucide-react';

function AppContent() {
  const { currentRoute, sidecarStatus, sidecarError } = useApp();

  if (sidecarStatus === 'searching') {
    return (
      <div className='flex h-screen w-screen flex-col items-center justify-center bg-gray-900 text-white'>
        <Loader2 className='h-12 w-12 animate-spin text-blue-500' />
        <p className='mt-4 text-xl font-medium text-gray-300'>Connecting to Sidecar...</p>
        <p className='mt-2 text-sm text-gray-500'>Initializing AI Brain</p>
      </div>
    );
  }

  if (sidecarStatus === 'error') {
    return (
      <div className='flex h-screen w-screen flex-col items-center justify-center bg-gray-900 p-6 text-center text-white'>
        <AlertCircle className='h-16 w-16 text-red-500' />
        <h1 className='mt-6 text-2xl font-bold'>Sidecar Connection Failed</h1>
        <p className='mt-4 max-w-md text-gray-400'>
          {sidecarError ||
            'The backend sidecar could not be reached. Please check if the application has the necessary permissions and restart it.'}
        </p>
        <button
          onClick={() => window.location.reload()}
          className='mt-8 rounded-lg bg-red-600 px-6 py-3 font-semibold text-white transition-colors hover:bg-red-500'
        >
          Retry Connection
        </button>
      </div>
    );
  }

  if (currentRoute === AppRoute.WELCOME) {
    return <Welcome />;
  }

  // Helper to determine visibility
  const getPageClass = (route: AppRoute) => {
    return currentRoute === route ? 'block h-full overflow-hidden' : 'hidden';
  };

  return (
    <Layout>
      <div className={getPageClass(AppRoute.HOME)}>
        <Home />
      </div>
      <div className={getPageClass(AppRoute.ROADMAP)}>
        <Roadmap />
      </div>
      <div className={getPageClass(AppRoute.CHAT)}>
        <Chat />
      </div>
      <div className={getPageClass(AppRoute.SETTINGS)}>
        <Settings />
      </div>
    </Layout>
  );
}

export default function App() {
  return <AppContent />;
}
