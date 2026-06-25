
import { useState } from 'react';
import { SidebarProvider, SidebarTrigger } from '@/components/ui/sidebar';
import { AdminSidebar } from '@/components/AdminSidebar';
import UserManagement from '@/components/UserManagement';
import GameManagement from '@/components/GameManagement';
import KeysManagement from '@/components/KeysManagement';
import OrdersManagement from '@/components/OrdersManagement';

const Admin = () => {
  const [activeSection, setActiveSection] = useState('dashboard');

  const renderContent = () => {
    switch (activeSection) {
      case 'users':
        return <UserManagement />;
      case 'games':
        return <GameManagement />;
      case 'keys':
        return <KeysManagement />;
      case 'orders':
        return <OrdersManagement />;
      default:
        return <UserManagement />;
    }
  };

  return (
    <SidebarProvider>
      <div className="min-h-screen flex w-full">
        <AdminSidebar 
          activeSection={activeSection} 
          onSectionChange={setActiveSection} 
        />
        <main className="flex-1 p-6">
          <div className="mb-4">
            <SidebarTrigger />
          </div>
          {renderContent()}
        </main>
      </div>
    </SidebarProvider>
  );
};

export default Admin;
