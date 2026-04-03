import {
  BrandIcon,
  ChatIcon,
  ExerciseIcon,
  HistoryIcon,
  PlusIcon,
  SettingsIcon,
} from "./Icons";

interface SidebarProps {
  onOpenHistory: () => void;
  onOpenAttach: () => void;
}

export function Sidebar({ onOpenHistory, onOpenAttach }: SidebarProps) {
  return (
    <aside className="sidebar">
      <div className="sidebar__brand">
        <div className="sidebar__brand-icon">
          <BrandIcon className="sidebar__brand-svg" />
        </div>
        <div>
          <h1>Cubik IA</h1>
          <p>Academic Curator</p>
        </div>
      </div>

      <nav className="sidebar__nav" aria-label="Navegacion principal">
        <button className="sidebar__nav-item is-active" type="button">
          <ChatIcon className="sidebar__nav-svg" />
          <span>Chat</span>
        </button>
        <button className="sidebar__nav-item" type="button" onClick={onOpenHistory}>
          <HistoryIcon className="sidebar__nav-svg" />
          <span>History</span>
        </button>
        <button className="sidebar__nav-item" type="button" onClick={onOpenAttach}>
          <ExerciseIcon className="sidebar__nav-svg" />
          <span>Exercises</span>
        </button>
        <button className="sidebar__nav-item" type="button">
          <SettingsIcon className="sidebar__nav-svg" />
          <span>Settings</span>
        </button>
      </nav>

      <button className="sidebar__cta" type="button" onClick={onOpenAttach}>
        <PlusIcon className="sidebar__cta-icon" />
        <span>New Exercise</span>
      </button>
    </aside>
  );
}
