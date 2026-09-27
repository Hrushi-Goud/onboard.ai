import { useState } from 'react';
import SummaryTab from './tabs/SummaryTab';
import ArchitectureTab from './tabs/ArchitectureTab';
import FileStructureTab from './tabs/FileStructureTab';
import SetupTab from './tabs/SetupTab';
import StarterTasksTab from './tabs/StarterTasksTab';
import OptimizationsTab from './tabs/OptimizationsTab';

const TABS = [
  { id: 'summary', label: 'Summary' },
  { id: 'architecture', label: 'Architecture' },
  { id: 'fileStructure', label: 'File Structure' },
  { id: 'setup', label: 'Setup Guide' },
  { id: 'starterTasks', label: 'Starter Tasks' },
  { id: 'optimizations', label: 'Optimizations' },
];

export default function ReportTabs({ report }) {
  const [active, setActive] = useState('summary');

  function renderPanel() {
    switch (active) {
      case 'summary':
        return <SummaryTab analysis={report.analysis} />;
      case 'architecture':
        return <ArchitectureTab architecture={report.architecture} />;
      case 'fileStructure':
        return <FileStructureTab analysis={report.analysis} />;
      case 'setup':
        return <SetupTab setupGuide={report.setup_guide} />;
      case 'starterTasks':
        return <StarterTasksTab tasks={report.starter_tasks_and_optimizations.starter_tasks} />;
      case 'optimizations':
        return <OptimizationsTab optimizations={report.starter_tasks_and_optimizations.optimizations} />;
      default:
        return null;
    }
  }

  return (
    <div>
      <div className="tab-bar" role="tablist">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            role="tab"
            aria-selected={active === tab.id}
            className={`tab-btn${active === tab.id ? ' active' : ''}`}
            onClick={() => setActive(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>
      <div className="tab-content" role="tabpanel">
        {renderPanel()}
      </div>
    </div>
  );
}
