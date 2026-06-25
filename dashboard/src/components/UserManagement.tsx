
import { useState, useEffect, useRef } from 'react';
import dayjs from 'dayjs';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { useToast } from '@/hooks/use-toast';
import { getAllUsers, setBanStatus, updateBalance, setVipStatus } from '@/api';
import {
  Search,
  ChevronLeft,
  ChevronRight,
  Ban,
  ShieldCheck,
  DollarSign,
  X,
  Calendar,
  ShoppingCart,
  TrendingUp,
  Hash,
  Crown,
  Globe,
  AtSign,
  UserIcon,
  Users,
} from 'lucide-react';

interface User {
  id: number;
  user_id: number;
  username: string | null;
  first_name: string | null;
  last_name: string | null;
  lang: string;
  register_at: string;
  balance: number;
  total_order: number;
  total_spent: number;
  total_invited: number;
  is_admin: boolean;
  is_banned: boolean;
  is_vip: boolean;
}

const AVATAR_URL = 'http://127.0.0.1:1337/api/users';

const getToken = (name: string = 'access_token'): string | null => {
  const cookies = document.cookie.split(';').map(c => c.trim());
  for (const cookie of cookies) {
    if (cookie.startsWith(`${name}=`)) {
      return cookie.substring(name.length + 1);
    }
  }
  return null;
};

const UserAvatar = ({ user, size = 36 }: { user: User; size?: number }) => {
  const [failed, setFailed] = useState(false);
  const initial = user.first_name ? user.first_name[0].toUpperCase() : '#';
  const token = getToken();

  if (failed || !token) {
    return (
      <div
        className="rounded-full bg-muted flex items-center justify-center font-medium shrink-0"
        style={{ width: size, height: size, fontSize: size * 0.38 }}
      >
        {initial}
      </div>
    );
  }

  return (
    <img
      src={`${AVATAR_URL}/${user.user_id}/avatar/?token=${token}`}
      alt=""
      className="rounded-full object-cover shrink-0 bg-muted"
      style={{ width: size, height: size }}
      onError={() => setFailed(true)}
    />
  );
};

const UserManagement = () => {
  const [searchId, setSearchId] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [balanceAmount, setBalanceAmount] = useState('');
  const [showBanDialog, setShowBanDialog] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    const fetchUsers = async () => {
      setLoading(true);
      try {
        setUsers(await getAllUsers());
      } catch {
        toast({ title: 'Failed to load users', variant: 'destructive' });
      } finally {
        setLoading(false);
      }
    };
    fetchUsers();
  }, []);

  const usersPerPage = 12;
  const sortedUsers = [...users].sort((a, b) => a.id - b.id);
  const filtered = searchId
    ? sortedUsers.filter(
        u =>
          u.user_id.toString().includes(searchId) ||
          (u.username && u.username.toLowerCase().includes(searchId.toLowerCase())) ||
          (u.first_name && u.first_name.toLowerCase().includes(searchId.toLowerCase()))
      )
    : sortedUsers;
  const totalPages = Math.ceil(filtered.length / usersPerPage);
  const startIndex = (currentPage - 1) * usersPerPage;
  const currentUsers = filtered.slice(startIndex, startIndex + usersPerPage);

  const updateUser = (userId: number, patch: Partial<User>) => {
    setUsers(prev => prev.map(u => (u.user_id === userId ? { ...u, ...patch } : u)));
    if (selectedUser?.user_id === userId) {
      setSelectedUser({ ...selectedUser, ...patch });
    }
  };

  const handleBanToggle = async (user: User) => {
    const newStatus = !user.is_banned;
    try {
      await setBanStatus(user.user_id, newStatus);
      updateUser(user.user_id, { is_banned: newStatus });
      toast({
        title: newStatus ? 'User Banned' : 'User Unbanned',
        description: `${displayName(user)} is now ${newStatus ? 'banned' : 'active'}`,
      });
    } catch {
      toast({ title: 'Failed to update status', variant: 'destructive' });
    }
    setShowBanDialog(false);
  };

  const handleVipToggle = async (user: User) => {
    const newStatus = !user.is_vip;
    try {
      await setVipStatus(user.user_id, newStatus);
      updateUser(user.user_id, { is_vip: newStatus });
      toast({
        title: newStatus ? 'VIP Granted' : 'VIP Revoked',
        description: `${displayName(user)} is now ${newStatus ? 'VIP' : 'regular'}`,
      });
    } catch {
      toast({ title: 'Failed to update VIP status', variant: 'destructive' });
    }
  };

  const handleBalanceAdjust = async (userId: number, operation: 'add' | 'subtract') => {
    const amountNum = Number(balanceAmount);
    if (!balanceAmount || isNaN(amountNum) || amountNum <= 0) {
      toast({ title: 'Enter a valid amount', variant: 'destructive' });
      return;
    }
    const operator = operation === 'add' ? '+' : '-';
    try {
      await updateBalance(userId, amountNum, operator);
      const user = users.find(u => u.user_id === userId);
      if (user) {
        const newBal = Math.max(
          0,
          operation === 'add' ? user.balance + amountNum : user.balance - amountNum
        );
        updateUser(userId, { balance: newBal });
      }
      toast({
        title: 'Balance Updated',
        description: `${operation === 'add' ? '+' : '-'}${amountNum}$`,
      });
      setBalanceAmount('');
    } catch {
      toast({ title: 'Failed to update balance', variant: 'destructive' });
    }
  };

  const displayName = (user: User) => {
    if (user.first_name) return user.first_name;
    if (user.username) return `@${user.username}`;
    return user.user_id.toString();
  };

  const fullName = (user: User) => {
    const parts = [user.first_name, user.last_name].filter(Boolean);
    return parts.length > 0 ? parts.join(' ') : '—';
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Users</h1>
          <p className="text-sm text-muted-foreground">
            {users.length} total · {users.filter(u => u.is_vip).length} VIP · {users.filter(u => u.is_banned).length} banned
          </p>
        </div>
      </div>

      <div className="relative max-w-sm">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
        <Input
          placeholder="Search by ID, username or name..."
          value={searchId}
          onChange={e => {
            setSearchId(e.target.value);
            setCurrentPage(1);
          }}
          className="pl-9"
        />
      </div>

      <div className="flex gap-6">
        {/* User list */}
        <div className="flex-1 space-y-1.5">
          {loading ? (
            <div className="text-center py-12 text-muted-foreground">Loading...</div>
          ) : currentUsers.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">No users found</div>
          ) : (
            currentUsers.map(user => (
              <div
                key={user.user_id}
                onClick={() => setSelectedUser(user)}
                className={`flex items-center justify-between p-3 rounded-lg border cursor-pointer transition-colors
                  ${
                    selectedUser?.user_id === user.user_id
                      ? 'border-primary bg-accent'
                      : 'border-border hover:bg-accent/50'
                  }`}
              >
                <div className="flex items-center gap-3">
                  <UserAvatar user={user} size={36} />
                  <div className="min-w-0">
                    <div className="flex items-center gap-1.5">
                      <span className="font-medium truncate">{displayName(user)}</span>
                      {user.is_vip && <Crown className="w-3.5 h-3.5 text-yellow-500 shrink-0" />}
                      {user.is_admin && <ShieldCheck className="w-3.5 h-3.5 text-blue-500 shrink-0" />}
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {user.username ? `@${user.username}` : `ID: ${user.user_id}`}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <span className="text-sm tabular-nums">{user.balance.toFixed(2)}$</span>
                  {user.is_banned && (
                    <Badge variant="destructive" className="text-xs">
                      Banned
                    </Badge>
                  )}
                </div>
              </div>
            ))
          )}

          {totalPages > 1 && (
            <div className="flex items-center justify-between pt-2">
              <span className="text-xs text-muted-foreground">
                Page {currentPage} of {totalPages}
              </span>
              <div className="flex gap-1">
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8"
                  onClick={() => setCurrentPage(p => Math.max(p - 1, 1))}
                  disabled={currentPage === 1}
                >
                  <ChevronLeft className="w-4 h-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8"
                  onClick={() => setCurrentPage(p => Math.min(p + 1, totalPages))}
                  disabled={currentPage === totalPages}
                >
                  <ChevronRight className="w-4 h-4" />
                </Button>
              </div>
            </div>
          )}
        </div>

        {/* User detail panel */}
        <div className="w-[380px] shrink-0">
          {selectedUser ? (
            <Card className="sticky top-6">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg">User Profile</CardTitle>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-7 w-7"
                    onClick={() => setSelectedUser(null)}
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-5">
                {/* Header */}
                <div className="flex items-center gap-3">
                  <UserAvatar user={selectedUser} size={56} />
                  <div className="min-w-0">
                    <div className="flex items-center gap-1.5">
                      <span className="font-semibold text-lg truncate">{fullName(selectedUser)}</span>
                      {selectedUser.is_vip && <Crown className="w-4 h-4 text-yellow-500 shrink-0" />}
                    </div>
                    {selectedUser.username && (
                      <div className="text-sm text-muted-foreground">@{selectedUser.username}</div>
                    )}
                    <div className="flex items-center gap-2 mt-1">
                      {selectedUser.is_banned ? (
                        <Badge variant="destructive" className="text-xs">Banned</Badge>
                      ) : (
                        <Badge variant="default" className="text-xs">Active</Badge>
                      )}
                      {selectedUser.is_admin && (
                        <Badge variant="secondary" className="text-xs">Admin</Badge>
                      )}
                    </div>
                  </div>
                </div>

                {/* Info grid */}
                <div className="grid grid-cols-2 gap-y-2.5 text-sm border-t pt-4">
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <Hash className="w-3.5 h-3.5" /> User ID
                  </div>
                  <div className="text-right font-mono text-xs">{selectedUser.user_id}</div>

                  <div className="flex items-center gap-2 text-muted-foreground">
                    <DollarSign className="w-3.5 h-3.5" /> Balance
                  </div>
                  <div className="text-right font-medium">{selectedUser.balance.toFixed(2)}$</div>

                  <div className="flex items-center gap-2 text-muted-foreground">
                    <TrendingUp className="w-3.5 h-3.5" /> Total Spent
                  </div>
                  <div className="text-right">{selectedUser.total_spent.toFixed(2)}$</div>

                  <div className="flex items-center gap-2 text-muted-foreground">
                    <ShoppingCart className="w-3.5 h-3.5" /> Orders
                  </div>
                  <div className="text-right">{selectedUser.total_order}</div>

                  <div className="flex items-center gap-2 text-muted-foreground">
                    <Users className="w-3.5 h-3.5" /> Referrals
                  </div>
                  <div className="text-right">{selectedUser.total_invited}</div>

                  <div className="flex items-center gap-2 text-muted-foreground">
                    <Calendar className="w-3.5 h-3.5" /> Registered
                  </div>
                  <div className="text-right">{dayjs(selectedUser.register_at).format('DD.MM.YYYY HH:mm')}</div>

                  <div className="flex items-center gap-2 text-muted-foreground">
                    <Globe className="w-3.5 h-3.5" /> Language
                  </div>
                  <div className="text-right">{selectedUser.lang.toUpperCase()}</div>
                </div>

                {/* Balance adjust */}
                <div className="space-y-2 border-t pt-4">
                  <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    Adjust Balance
                  </label>
                  <Input
                    type="number"
                    placeholder="Amount"
                    value={balanceAmount}
                    onChange={e => setBalanceAmount(e.target.value)}
                    min="0"
                    step="1"
                  />
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      className="flex-1"
                      disabled={!balanceAmount || Number(balanceAmount) <= 0}
                      onClick={() => handleBalanceAdjust(selectedUser.user_id, 'add')}
                    >
                      + Add
                    </Button>
                    <Button
                      size="sm"
                      variant="destructive"
                      className="flex-1"
                      disabled={!balanceAmount || Number(balanceAmount) <= 0}
                      onClick={() => handleBalanceAdjust(selectedUser.user_id, 'subtract')}
                    >
                      − Subtract
                    </Button>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex gap-2 border-t pt-4">
                  <Button
                    variant={selectedUser.is_vip ? 'secondary' : 'outline'}
                    className="flex-1"
                    size="sm"
                    onClick={() => handleVipToggle(selectedUser)}
                  >
                    <Crown className={`w-4 h-4 ${selectedUser.is_vip ? 'text-yellow-500' : ''}`} />
                    {selectedUser.is_vip ? 'Revoke VIP' : 'Grant VIP'}
                  </Button>
                  <Button
                    variant={selectedUser.is_banned ? 'default' : 'destructive'}
                    className="flex-1"
                    size="sm"
                    onClick={() => setShowBanDialog(true)}
                  >
                    {selectedUser.is_banned ? (
                      <><ShieldCheck className="w-4 h-4" /> Unban</>
                    ) : (
                      <><Ban className="w-4 h-4" /> Ban</>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className="flex flex-col items-center justify-center h-64 text-muted-foreground text-sm border border-dashed rounded-lg gap-2">
              <UserIcon className="w-8 h-8 opacity-40" />
              Select a user to view details
            </div>
          )}
        </div>
      </div>

      {/* Ban confirmation */}
      <AlertDialog open={showBanDialog} onOpenChange={setShowBanDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>
              {selectedUser?.is_banned ? 'Unban User' : 'Ban User'}
            </AlertDialogTitle>
            <AlertDialogDescription>
              {selectedUser?.is_banned
                ? `Unban ${selectedUser ? displayName(selectedUser) : ''}? They will regain access.`
                : `Ban ${selectedUser ? displayName(selectedUser) : ''}? They will lose access.`}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={() => selectedUser && handleBanToggle(selectedUser)}>
              {selectedUser?.is_banned ? 'Unban' : 'Ban'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default UserManagement;
