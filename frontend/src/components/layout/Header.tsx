import { useWebSocket } from '../../context/WebSocketContext.tsx';
import UserProfileDropdown from './UserProfileDropdown.tsx';

export default function Header() {
  const { status } = useWebSocket();

  const statusColor =
    status === 'connected'
      ? 'bg-success'
      : status === 'connecting'
        ? 'bg-warning'
        : 'bg-danger';

  return (
    <header className="bg-black h-16 flex items-center justify-between px-6 shrink-0 shadow-md">
      <div className="flex items-center gap-3">
        <img src="/bullmqr-logo.png" alt="BuLLMQR" className="h-14" />
      </div>

      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 text-sm text-white/80">
          <span className={`inline-block w-2 h-2 rounded-full ${statusColor}`} />
          {status === 'connected' ? 'Live' : status === 'connecting' ? 'Connecting...' : 'Offline'}
        </div>

        <UserProfileDropdown />
      </div>
    </header>
  );
}
