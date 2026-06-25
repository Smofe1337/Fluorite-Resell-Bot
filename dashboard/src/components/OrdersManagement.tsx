
import { useState, useEffect } from 'react';
import dayjs from 'dayjs';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
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
import { getAllOrders, updateOrderStatus, getOrdersStats } from '@/api';
import {
  Search,
  ChevronLeft,
  ChevronRight,
  X,
  Copy,
  DollarSign,
  Clock,
  CreditCard,
  Gamepad2,
  Hash,
  Link,
  Calendar,
  Package,
  Gift,
  ExternalLink,
  ShoppingCart,
  CheckCircle,
  XCircle,
  AlertCircle,
} from 'lucide-react';

interface Order {
  id: number;
  user_id: number;
  order_id: string;
  game_name: string | null;
  duration: number | null;
  sum: number;
  payment_system_order_id: string;
  pay_url: string;
  order_type: string;
  payment_method: string;
  create_at: string;
  expired_at: string;
  status: string;
  is_gift: boolean | null;
  product: string | null;
}

interface Stats {
  total: number;
  paid: number;
  pending: number;
  cancelled: number;
  revenue: number;
}

const statusColors: Record<string, string> = {
  Paid: 'bg-green-500/15 text-green-400 border-green-500/30',
  Pending: 'bg-yellow-500/15 text-yellow-400 border-yellow-500/30',
  Cancelled: 'bg-red-500/15 text-red-400 border-red-500/30',
  Expired: 'bg-gray-500/15 text-gray-400 border-gray-500/30',
  Error: 'bg-red-500/15 text-red-400 border-red-500/30',
};

const statusOptions = ['Pending', 'Paid', 'Cancelled', 'Expired', 'Error'];

const OrdersManagement = () => {
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [orders, setOrders] = useState<Order[]>([]);
  const [totalPages, setTotalPages] = useState(1);
  const [totalOrders, setTotalOrders] = useState(0);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);
  const [showStatusDialog, setShowStatusDialog] = useState(false);
  const [newStatus, setNewStatus] = useState('');
  const { toast } = useToast();

  const fetchOrders = async (page: number, searchQuery: string, status: string) => {
    setLoading(true);
    try {
      const data = await getAllOrders(page, 15, searchQuery || undefined, status !== 'all' ? status : undefined);
      setOrders(data.orders || []);
      setTotalPages(data.total_pages || 1);
      setTotalOrders(data.total || 0);
    } catch {
      toast({ title: 'Failed to load orders', variant: 'destructive' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    getOrdersStats().then(setStats).catch(() => {});
  }, []);

  useEffect(() => {
    fetchOrders(currentPage, search, statusFilter);
  }, [currentPage, statusFilter]);

  useEffect(() => {
    const timeout = setTimeout(() => {
      setCurrentPage(1);
      fetchOrders(1, search, statusFilter);
    }, 300);
    return () => clearTimeout(timeout);
  }, [search]);

  const currentOrders = orders;

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text).then(() => toast({ title: 'Copied!' }));
  };

  const handleStatusUpdate = async () => {
    if (!selectedOrder || !newStatus) return;
    try {
      await updateOrderStatus(selectedOrder.order_id, newStatus);
      setSelectedOrder({ ...selectedOrder, status: newStatus });
      toast({ title: 'Status Updated', description: `${selectedOrder.order_id} → ${newStatus}` });
      await fetchOrders(currentPage, search, statusFilter);
      getOrdersStats().then(setStats).catch(() => {});
    } catch {
      toast({ title: 'Failed to update status', variant: 'destructive' });
    }
    setShowStatusDialog(false);
    setNewStatus('');
  };

  const formatDate = (d: string) => dayjs(d).format('DD.MM.YYYY HH:mm');

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Orders</h1>
          <p className="text-sm text-muted-foreground">{totalOrders} total orders</p>
        </div>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-4 gap-3">
          <div className="border rounded-lg p-3">
            <div className="text-xs text-muted-foreground">Revenue</div>
            <div className="text-lg font-bold">{stats.revenue.toFixed(2)}$</div>
          </div>
          <div className="border rounded-lg p-3">
            <div className="text-xs text-muted-foreground">Paid</div>
            <div className="text-lg font-bold text-green-400">{stats.paid}</div>
          </div>
          <div className="border rounded-lg p-3">
            <div className="text-xs text-muted-foreground">Pending</div>
            <div className="text-lg font-bold text-yellow-400">{stats.pending}</div>
          </div>
          <div className="border rounded-lg p-3">
            <div className="text-xs text-muted-foreground">Cancelled</div>
            <div className="text-lg font-bold text-red-400">{stats.cancelled}</div>
          </div>
        </div>
      )}

      {/* Search + filter */}
      <div className="flex gap-3">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            placeholder="Search by order ID, user ID or game..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>
        <Select value={statusFilter} onValueChange={v => { setStatusFilter(v); setCurrentPage(1); } }>
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
        {/* Order list */}
        <div className="flex-1 space-y-1.5">
          {loading ? (
            <div className="text-center py-12 text-muted-foreground">Loading...</div>
          ) : currentOrders.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">No orders found</div>
          ) : (
            currentOrders.map(order => (
              <div
                key={order.order_id}
                onClick={() => setSelectedOrder(order)}
                className={`flex items-center justify-between p-3 rounded-lg border cursor-pointer transition-colors
                  ${selectedOrder?.order_id === order.order_id
                    ? 'border-primary bg-accent'
                    : 'border-border hover:bg-accent/50'
                  }`}
              >
                <div className="flex items-center gap-3 min-w-0">
                  <div className="w-9 h-9 rounded-full bg-muted flex items-center justify-center shrink-0">
                    {order.is_gift ? (
                      <Gift className="w-4 h-4 text-muted-foreground" />
                    ) : (
                      <ShoppingCart className="w-4 h-4 text-muted-foreground" />
                    )}
                  </div>
                  <div className="min-w-0">
                    <div className="flex items-center gap-1.5">
                      <span className="font-mono text-sm font-medium">{order.order_id}</span>
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {order.game_name || order.order_type} · {formatDate(order.create_at)}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <span className="text-sm tabular-nums font-medium">{order.sum.toFixed(2)}$</span>
                  <Badge variant="outline" className={`text-xs ${statusColors[order.status] || ''}`}>
                    {order.status}
                  </Badge>
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

        {/* Detail panel */}
        <div className="w-[400px] shrink-0">
          {selectedOrder ? (
            <Card className="sticky top-6">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg">Order Details</CardTitle>
                  <Button variant="ghost" size="icon" className="h-7 w-7"
                    onClick={() => setSelectedOrder(null)}>
                    <X className="w-4 h-4" />
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Header */}
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-mono font-semibold">{selectedOrder.order_id}</div>
                    <div className="text-xs text-muted-foreground">{selectedOrder.order_type}</div>
                  </div>
                  <Badge variant="outline" className={`${statusColors[selectedOrder.status] || ''}`}>
                    {selectedOrder.status}
                  </Badge>
                </div>

                {/* Info */}
                <div className="grid grid-cols-2 gap-y-2.5 text-sm border-t pt-4">
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <Hash className="w-3.5 h-3.5" /> User ID
                  </div>
                  <div className="text-right font-mono text-xs">{selectedOrder.user_id}</div>

                  <div className="flex items-center gap-2 text-muted-foreground">
                    <DollarSign className="w-3.5 h-3.5" /> Amount
                  </div>
                  <div className="text-right font-medium">{selectedOrder.sum.toFixed(2)}$</div>

                  <div className="flex items-center gap-2 text-muted-foreground">
                    <CreditCard className="w-3.5 h-3.5" /> Payment
                  </div>
                  <div className="text-right">{selectedOrder.payment_method}</div>

                  {selectedOrder.game_name && (
                    <>
                      <div className="flex items-center gap-2 text-muted-foreground">
                        <Gamepad2 className="w-3.5 h-3.5" /> Game
                      </div>
                      <div className="text-right">{selectedOrder.game_name}</div>
                    </>
                  )}

                  {selectedOrder.duration && (
                    <>
                      <div className="flex items-center gap-2 text-muted-foreground">
                        <Clock className="w-3.5 h-3.5" /> Duration
                      </div>
                      <div className="text-right">{selectedOrder.duration} days</div>
                    </>
                  )}

                  <div className="flex items-center gap-2 text-muted-foreground">
                    <Calendar className="w-3.5 h-3.5" /> Created
                  </div>
                  <div className="text-right text-xs">{formatDate(selectedOrder.create_at)}</div>

                  <div className="flex items-center gap-2 text-muted-foreground">
                    <Clock className="w-3.5 h-3.5" /> Expires
                  </div>
                  <div className="text-right text-xs">{formatDate(selectedOrder.expired_at)}</div>

                  {selectedOrder.product && (
                    <>
                      <div className="flex items-center gap-2 text-muted-foreground">
                        <Package className="w-3.5 h-3.5" /> Product
                      </div>
                      <div className="text-right text-xs font-mono truncate">{selectedOrder.product}</div>
                    </>
                  )}
                </div>

                {/* IDs */}
                <div className="space-y-2 border-t pt-4">
                  <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    External ID
                  </label>
                  <div className="flex items-center gap-2">
                    <code className="flex-1 text-xs bg-muted px-2 py-1.5 rounded truncate">
                      {selectedOrder.payment_system_order_id}
                    </code>
                    <Button variant="ghost" size="icon" className="h-7 w-7 shrink-0"
                      onClick={() => handleCopy(selectedOrder.payment_system_order_id)}>
                      <Copy className="w-3.5 h-3.5" />
                    </Button>
                  </div>
                </div>

                {selectedOrder.pay_url && (
                  <div className="space-y-2">
                    <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                      Payment URL
                    </label>
                    <div className="flex items-center gap-2">
                      <code className="flex-1 text-xs bg-muted px-2 py-1.5 rounded truncate">
                        {selectedOrder.pay_url}
                      </code>
                      <Button variant="ghost" size="icon" className="h-7 w-7 shrink-0"
                        onClick={() => handleCopy(selectedOrder.pay_url)}>
                        <Copy className="w-3.5 h-3.5" />
                      </Button>
                    </div>
                  </div>
                )}

                {/* Badges */}
                {selectedOrder.is_gift && (
                  <Badge variant="secondary" className="text-xs">
                    <Gift className="w-3 h-3 mr-1" /> Gift Order
                  </Badge>
                )}

                {/* Status change */}
                <div className="border-t pt-4">
                  <Button
                    variant="outline"
                    className="w-full"
                    size="sm"
                    onClick={() => { setNewStatus(selectedOrder.status); setShowStatusDialog(true); }}
                  >
                    Change Status
                  </Button>
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className="flex flex-col items-center justify-center h-64 text-muted-foreground text-sm border border-dashed rounded-lg gap-2">
              <Package className="w-8 h-8 opacity-40" />
              Select an order to view details
            </div>
          )}
        </div>
      </div>

      {/* Status dialog */}
      <AlertDialog open={showStatusDialog} onOpenChange={setShowStatusDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Change Order Status</AlertDialogTitle>
            <AlertDialogDescription>
              Update status for order {selectedOrder?.order_id}
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
              disabled={!newStatus || newStatus === selectedOrder?.status}
            >
              Update
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default OrdersManagement;
