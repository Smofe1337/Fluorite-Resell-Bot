
import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
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
import {
  Search,
  ChevronLeft,
  ChevronRight,
  X,
  Copy,
  Key,
  Gamepad2,
  Clock,
  Hash,
  User,
  Plus,
  Upload,
  Trash2,
  Shield,
} from 'lucide-react';
import { getAllKeys, addKeys, deleteKey, getAllGames, getKeysStats, updateKeyStatus } from '@/api';
import { useToast } from '@/hooks/use-toast';

interface LicenseKey {
  id: number;
  owner_id: number | null;
  key: string;
  game: string;
  duration: number;
  token: string | null;
  status: string;
}

interface Game {
  id: number;
  name: string;
}

interface Stats {
  total: number;
  available: number;
  sold: number;
  pending: number;
  received: number;
  by_game: Record<string, { total: number; available: number }>;
}

const statusColors: Record<string, string> = {
  Available: 'bg-green-500/15 text-green-400 border-green-500/30',
  Sold: 'bg-blue-500/15 text-blue-400 border-blue-500/30',
  Pending: 'bg-yellow-500/15 text-yellow-400 border-yellow-500/30',
  Received: 'bg-gray-500/15 text-gray-400 border-gray-500/30',
};

const durationLabels: Record<number, string> = {
  1: '1 Day',
  7: '7 Days',
  30: '30 Days',
};

const statusOptions = ['Available', 'Sold', 'Pending', 'Received'];

const KeysManagement = () => {
  const [keys, setKeys] = useState<LicenseKey[]>([]);
  const [games, setGames] = useState<Game[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedKey, setSelectedKey] = useState<LicenseKey | null>(null);

  const [search, setSearch] = useState('');
  const [filterGame, setFilterGame] = useState('all');
  const [filterDuration, setFilterDuration] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');
  const [currentPage, setCurrentPage] = useState(1);

  const [showAddDialog, setShowAddDialog] = useState(false);
  const [addGame, setAddGame] = useState('');
  const [addDuration, setAddDuration] = useState<number | null>(null);
  const [addKeysInput, setAddKeysInput] = useState('');

  const [showStatusDialog, setShowStatusDialog] = useState(false);
  const [newStatus, setNewStatus] = useState('');

  const [showDeleteDialog, setShowDeleteDialog] = useState(false);

  const { toast } = useToast();

  const fetchData = async () => {
    setLoading(true);
    try {
      const [keysData, gamesData, statsData] = await Promise.all([
        getAllKeys(),
        getAllGames(),
        getKeysStats(),
      ]);
      setKeys(keysData);
      setGames(gamesData);
      setStats(statsData);
    } catch {
      toast({ title: 'Failed to load data', variant: 'destructive' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const keysPerPage = 20;
  const sorted = [...keys].sort((a, b) => b.id - a.id);
  const filtered = sorted.filter(k => {
    const matchesSearch = !search ||
      k.key.toLowerCase().includes(search.toLowerCase()) ||
      k.game.toLowerCase().includes(search.toLowerCase()) ||
      k.id.toString().includes(search);
    const matchesGame = filterGame === 'all' || k.game === filterGame;
    const matchesDuration = filterDuration === 'all' || k.duration.toString() === filterDuration;
    const matchesStatus = filterStatus === 'all' || k.status === filterStatus;
    return matchesSearch && matchesGame && matchesDuration && matchesStatus;
  });
  const totalPages = Math.ceil(filtered.length / keysPerPage);
  const startIndex = (currentPage - 1) * keysPerPage;
  const currentKeys = filtered.slice(startIndex, startIndex + keysPerPage);

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text).then(() => toast({ title: 'Copied!' }));
  };

  const handleAddKeys = async () => {
    if (!addGame || !addDuration || !addKeysInput.trim()) return;
    const selectedGameObj = games.find(g => g.id.toString() === addGame);
    if (!selectedGameObj) return;

    const keysList = addKeysInput
      .split('\n')
      .map(k => k.trim())
      .filter(k => k.length > 0);

    try {
      const response = await addKeys(selectedGameObj.name, addDuration, keysList);
      if (response.status === 409) {
        toast({ title: 'Keys already exist', variant: 'destructive' });
        return;
      }
      setKeys(prev => [...prev, ...response]);
      toast({ title: 'Success', description: `${keysList.length} keys added` });
      setShowAddDialog(false);
      setAddKeysInput('');
      setAddGame('');
      setAddDuration(null);
      const statsData = await getKeysStats();
      setStats(statsData);
    } catch {
      toast({ title: 'Failed to add keys', variant: 'destructive' });
    }
  };

  const handleLoadFile = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.txt';
    input.onchange = () => {
      const file = input.files?.[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
          const content = e.target?.result as string;
          const fileKeys = content.split('\n').map(k => k.trim()).filter(k => k.length > 0);
          setAddKeysInput(fileKeys.join('\n'));
        };
        reader.readAsText(file);
      }
    };
    input.click();
  };

  const handleDelete = async () => {
    if (!selectedKey) return;
    try {
      await deleteKey(selectedKey.key);
      setKeys(prev => prev.filter(k => k.key !== selectedKey.key));
      setSelectedKey(null);
      toast({ title: 'Key deleted' });
      setShowDeleteDialog(false);
      const statsData = await getKeysStats();
      setStats(statsData);
    } catch {
      toast({ title: 'Failed to delete key', variant: 'destructive' });
    }
  };

  const handleStatusUpdate = async () => {
    if (!selectedKey || !newStatus) return;
    try {
      await updateKeyStatus(selectedKey.key, newStatus);
      setKeys(prev =>
        prev.map(k => k.key === selectedKey.key ? { ...k, status: newStatus } : k)
      );
      setSelectedKey({ ...selectedKey, status: newStatus });
      toast({ title: 'Status Updated', description: `${selectedKey.key.slice(0, 20)}… → ${newStatus}` });
      const statsData = await getKeysStats();
      setStats(statsData);
    } catch {
      toast({ title: 'Failed to update status', variant: 'destructive' });
    }
    setShowStatusDialog(false);
    setNewStatus('');
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Keys</h1>
          <p className="text-sm text-muted-foreground">{keys.length} total keys</p>
        </div>
        <Button onClick={() => setShowAddDialog(true)}>
          <Plus className="w-4 h-4" />
          Add Keys
        </Button>
      </div>

      {stats && (
        <div className="grid grid-cols-4 gap-3">
          <div className="border rounded-lg p-3">
            <div className="text-xs text-muted-foreground">Total</div>
            <div className="text-lg font-bold">{stats.total}</div>
          </div>
          <div className="border rounded-lg p-3">
            <div className="text-xs text-muted-foreground">Available</div>
            <div className="text-lg font-bold text-green-400">{stats.available}</div>
          </div>
          <div className="border rounded-lg p-3">
            <div className="text-xs text-muted-foreground">Sold</div>
            <div className="text-lg font-bold text-blue-400">{stats.sold}</div>
          </div>
          <div className="border rounded-lg p-3">
            <div className="text-xs text-muted-foreground">Pending</div>
            <div className="text-lg font-bold text-yellow-400">{stats.pending}</div>
          </div>
        </div>
      )}

      <div className="flex gap-3">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            placeholder="Search by key, game or ID..."
            value={search}
            onChange={e => { setSearch(e.target.value); setCurrentPage(1); }}
            className="pl-9"
          />
        </div>
        <Select value={filterGame} onValueChange={v => { setFilterGame(v); setCurrentPage(1); }}>
          <SelectTrigger className="w-[150px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All games</SelectItem>
            {Array.from(new Set(keys.map(k => k.game))).map(g => (
              <SelectItem key={g} value={g}>{g}</SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select value={filterDuration} onValueChange={v => { setFilterDuration(v); setCurrentPage(1); }}>
          <SelectTrigger className="w-[130px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All durations</SelectItem>
            <SelectItem value="1">1 Day</SelectItem>
            <SelectItem value="7">7 Days</SelectItem>
            <SelectItem value="30">30 Days</SelectItem>
          </SelectContent>
        </Select>
        <Select value={filterStatus} onValueChange={v => { setFilterStatus(v); setCurrentPage(1); }}>
          <SelectTrigger className="w-[140px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All statuses</SelectItem>
            {statusOptions.map(s => (
              <SelectItem key={s} value={s}>{s}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="flex gap-6">
        <div className="flex-1 space-y-1.5">
          {loading ? (
            <div className="text-center py-12 text-muted-foreground">Loading...</div>
          ) : currentKeys.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">No keys found</div>
          ) : (
            currentKeys.map(k => (
              <div
                key={k.id}
                onClick={() => setSelectedKey(k)}
                className={`flex items-center justify-between p-3 rounded-lg border cursor-pointer transition-colors
                  ${selectedKey?.id === k.id
                    ? 'border-primary bg-accent'
                    : 'border-border hover:bg-accent/50'
                  }`}
              >
                <div className="flex items-center gap-3 min-w-0">
                  <div className="w-9 h-9 rounded-full bg-muted flex items-center justify-center shrink-0">
                    <Key className="w-4 h-4 text-muted-foreground" />
                  </div>
                  <div className="min-w-0">
                    <div className="font-mono text-sm font-medium truncate max-w-[280px]">{k.key}</div>
                    <div className="text-xs text-muted-foreground">
                      {k.game} · {durationLabels[k.duration] || `${k.duration}d`}
                    </div>
                  </div>
                </div>
                <Badge variant="outline" className={`text-xs shrink-0 ${statusColors[k.status] || ''}`}>
                  {k.status}
                </Badge>
              </div>
            ))
          )}

          {totalPages > 1 && (
            <div className="flex items-center justify-between pt-2">
              <span className="text-xs text-muted-foreground">
                Page {currentPage} of {totalPages}
              </span>
              <div className="flex gap-1">
                <Button variant="ghost" size="icon" className="h-8 w-8"
                  onClick={() => setCurrentPage(p => Math.max(p - 1, 1))} disabled={currentPage === 1}>
                  <ChevronLeft className="w-4 h-4" />
                </Button>
                <Button variant="ghost" size="icon" className="h-8 w-8"
                  onClick={() => setCurrentPage(p => Math.min(p + 1, totalPages))} disabled={currentPage === totalPages}>
                  <ChevronRight className="w-4 h-4" />
                </Button>
              </div>
            </div>
          )}
        </div>

        <div className="w-[400px] shrink-0">
          {selectedKey ? (
            <Card className="sticky top-6">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg">Key Details</CardTitle>
                  <Button variant="ghost" size="icon" className="h-7 w-7"
                    onClick={() => setSelectedKey(null)}>
                    <X className="w-4 h-4" />
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="min-w-0 flex-1">
                    <div className="font-mono text-sm font-semibold truncate">{selectedKey.key}</div>
                    <div className="text-xs text-muted-foreground">ID: {selectedKey.id}</div>
                  </div>
                  <Badge variant="outline" className={`shrink-0 ${statusColors[selectedKey.status] || ''}`}>
                    {selectedKey.status}
                  </Badge>
                </div>

                <div className="space-y-2">
                  <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    License Key
                  </label>
                  <div className="flex items-center gap-2">
                    <code className="flex-1 text-xs bg-muted px-2 py-1.5 rounded truncate">
                      {selectedKey.key}
                    </code>
                    <Button variant="ghost" size="icon" className="h-7 w-7 shrink-0"
                      onClick={() => handleCopy(selectedKey.key)}>
                      <Copy className="w-3.5 h-3.5" />
                    </Button>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-y-2.5 text-sm border-t pt-4">
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <Hash className="w-3.5 h-3.5" /> ID
                  </div>
                  <div className="text-right font-mono text-xs">{selectedKey.id}</div>

                  <div className="flex items-center gap-2 text-muted-foreground">
                    <Gamepad2 className="w-3.5 h-3.5" /> Game
                  </div>
                  <div className="text-right">{selectedKey.game}</div>

                  <div className="flex items-center gap-2 text-muted-foreground">
                    <Clock className="w-3.5 h-3.5" /> Duration
                  </div>
                  <div className="text-right">{durationLabels[selectedKey.duration] || `${selectedKey.duration} days`}</div>

                  <div className="flex items-center gap-2 text-muted-foreground">
                    <Shield className="w-3.5 h-3.5" /> Status
                  </div>
                  <div className="text-right">{selectedKey.status}</div>

                  {selectedKey.owner_id && (
                    <>
                      <div className="flex items-center gap-2 text-muted-foreground">
                        <User className="w-3.5 h-3.5" /> Owner
                      </div>
                      <div className="text-right font-mono text-xs">{selectedKey.owner_id}</div>
                    </>
                  )}

                  {selectedKey.token && (
                    <div className="col-span-2 pt-2">
                      <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                        Token
                      </label>
                      <div className="flex items-center gap-2 mt-1">
                        <code className="flex-1 text-xs bg-muted px-2 py-1.5 rounded truncate">
                          {selectedKey.token}
                        </code>
                        <Button variant="ghost" size="icon" className="h-7 w-7 shrink-0"
                          onClick={() => handleCopy(selectedKey.token!)}>
                          <Copy className="w-3.5 h-3.5" />
                        </Button>
                      </div>
                    </div>
                  )}
                </div>

                <div className="border-t pt-4 space-y-2">
                  <Button
                    variant="outline"
                    className="w-full"
                    size="sm"
                    onClick={() => { setNewStatus(selectedKey.status); setShowStatusDialog(true); }}
                  >
                    Change Status
                  </Button>
                  <Button
                    variant="destructive"
                    className="w-full"
                    size="sm"
                    onClick={() => setShowDeleteDialog(true)}
                  >
                    <Trash2 className="w-4 h-4" />
                    Delete Key
                  </Button>
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className="flex flex-col items-center justify-center h-64 text-muted-foreground text-sm border border-dashed rounded-lg gap-2">
              <Key className="w-8 h-8 opacity-40" />
              Select a key to view details
            </div>
          )}
        </div>
      </div>

      <AlertDialog open={showAddDialog} onOpenChange={setShowAddDialog}>
        <AlertDialogContent className="max-w-md">
          <AlertDialogHeader>
            <AlertDialogTitle>Add Keys</AlertDialogTitle>
            <AlertDialogDescription>
              Add new license keys for a game
            </AlertDialogDescription>
          </AlertDialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>Game</Label>
              <Select value={addGame} onValueChange={setAddGame}>
                <SelectTrigger>
                  <SelectValue placeholder="Select game" />
                </SelectTrigger>
                <SelectContent>
                  {games.map(g => (
                    <SelectItem key={g.id} value={g.id.toString()}>{g.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Duration</Label>
              <Select value={addDuration?.toString() || ''} onValueChange={v => setAddDuration(Number(v))}>
                <SelectTrigger>
                  <SelectValue placeholder="Select duration" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1">1 Day</SelectItem>
                  <SelectItem value="7">7 Days</SelectItem>
                  <SelectItem value="30">30 Days</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label>Keys</Label>
                <Button variant="ghost" size="sm" className="h-7 text-xs" onClick={handleLoadFile}>
                  <Upload className="w-3 h-3" />
                  Load from file
                </Button>
              </div>
              <Textarea
                value={addKeysInput}
                onChange={e => setAddKeysInput(e.target.value)}
                placeholder="Enter keys, one per line..."
                className="min-h-32 font-mono text-xs"
              />
              {addKeysInput.trim() && (
                <p className="text-xs text-muted-foreground">
                  {addKeysInput.split('\n').filter(k => k.trim()).length} keys ready
                </p>
              )}
            </div>
          </div>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleAddKeys}
              disabled={!addGame || !addDuration || !addKeysInput.trim()}
            >
              Add Keys
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      <AlertDialog open={showStatusDialog} onOpenChange={setShowStatusDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Change Key Status</AlertDialogTitle>
            <AlertDialogDescription>
              Update status for key {selectedKey?.key.slice(0, 30)}...
            </AlertDialogDescription>
          </AlertDialogHeader>
          <Select value={newStatus} onValueChange={setNewStatus}>
            <SelectTrigger>
              <SelectValue placeholder="Select status..." />
            </SelectTrigger>
            <SelectContent>
              {statusOptions.map(s => (
                <SelectItem key={s} value={s}>{s}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleStatusUpdate}
              disabled={!newStatus || newStatus === selectedKey?.status}
            >
              Update
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Key</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete this key? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleDelete} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default KeysManagement;
