
import {
  User,
  Key,
  Book,
  Package,
  Sun,
  Moon
} from 'lucide-react';
import { useTheme } from 'next-themes';
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarHeader,
  SidebarFooter,
} from '@/components/ui/sidebar';

interface AdminSidebarProps {
  activeSection: string;
  onSectionChange: (section: string) => void;
}

const menuItems = [
  {
    id: 'users',
    title: 'User Management',
    icon: User,
  },
  {
    id: 'games',
    title: 'Game Management',
    icon: Book,
  },
  {
    id: 'keys',
    title: 'Keys Management',
    icon: Key,
  },
  {
    id: 'orders',
    title: 'Orders Management',
    icon: Package,
  }
  /*{
    id: 'broadcast',
    title: 'Broadcast',
    icon: MessageSquare,
  },*/
];

export function AdminSidebar({ activeSection, onSectionChange }: AdminSidebarProps) {
  const { theme, setTheme } = useTheme();

  return (
    <Sidebar className="border-r border-border">
      <SidebarHeader className="border-b border-border">
        <div className="flex items-center space-x-3 px-6 py-4">
          <div>
            <h2 className="font-semibold text-lg">FluoriteHub</h2>
            <p className="text-sm text-muted-foreground">Management</p>
          </div>
        </div>
      </SidebarHeader>
      
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              {menuItems.map((item) => (
                <SidebarMenuItem key={item.id}>
                  <SidebarMenuButton 
                    onClick={() => onSectionChange(item.id)}
                    isActive={activeSection === item.id}
                    className="w-full justify-start"
                  >
                    <item.icon className="w-4 h-4" />
                    <span>{item.title}</span>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="border-t border-border p-3">
        <button
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          className="flex items-center gap-2 w-full px-3 py-2 rounded-md text-sm text-muted-foreground hover:bg-accent hover:text-accent-foreground transition-colors"
        >
          {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          <span>{theme === 'dark' ? 'Light mode' : 'Dark mode'}</span>
        </button>
      </SidebarFooter>
    </Sidebar>
  );
}
