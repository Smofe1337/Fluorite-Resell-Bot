
import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { getAllGames, deleteGame, createGame, updateGame, updateVisibility, uploadImage } from '@/api';
import { useToast } from '@/hooks/use-toast';
import { Edit, Upload, X } from 'lucide-react';

const DEFAULT_IMAGE = 'http://127.0.0.1:1337/api/static/images/default.png';

interface Game {
  id: number;
  name: string;
  status: string;
  is_need_show_img: boolean;
  image_url: string;
  pricing: {
    price_day: number;
    price_week: number;
    price_month: number;
  };
}

const GameManagement = () => {
  const [games, setGames] = useState<Game[]>([]);
  const { toast } = useToast();
  
  useEffect(() => {
    const fetchGames = async () => {
      const rawGames = await getAllGames();

      const mappedGames: Game[] = rawGames.map((game: any) => ({
        id: game.id,
        name: game.name,
        status: game.status,
        image_url: game.screenshot,
        is_need_show_img: game.is_need_show_img,
        pricing: {
          price_day: game.pricing.oneDay,
          price_week: game.pricing.sevenDays,
          price_month: game.pricing.thirtyOneDays
        }
      }));

      setGames(mappedGames);
    };

    fetchGames();
  }, []);

  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [editingGame, setEditingGame] = useState<Game | null>(null);
  const [isConfirmDeleteOpen, setIsConfirmDeleteOpen] = useState(false);
  const [gameToDelete, setGameToDelete] = useState<Game | null>(null);
  const [uploading, setUploading] = useState(false);

  const handleUpload = async (file: File): Promise<string | null> => {
    setUploading(true);
    try {
      const url = await uploadImage(file);
      return url;
    } catch {
      toast({ title: 'Upload Failed', description: 'Failed to upload image', variant: 'destructive' });
      return null;
    } finally {
      setUploading(false);
    }
  };

  const [newGame, setNewGame] = useState({
    name: '',
    status: 'Safe',
    screenshot: '',
    pricing: { oneDay: 3, sevenDays: 15, thirtyOneDays: 25 },
  });

  const [editGame, setEditGame] = useState({
    name: '',
    status: 'Safe',
    screenshot: '',
    pricing: { oneDay: 0, sevenDays: 0, thirtyOneDays: 0 },
  });

  const handleCreateGame = async() => {
    try {
      const { name, screenshot, pricing, status } = newGame;

      if (!name.trim()) {
        toast({
          title: 'Validation Error',
          description: 'Game name is required',
          variant: 'destructive',
      });
      return;
      }

      const pricingData = {
        day: pricing.oneDay,
        week: pricing.sevenDays,
        month: pricing.thirtyOneDays
      };

      const response = await createGame(
        name.trim(),
        pricingData,
        screenshot || '',
        status,
        true
      );

      const createdGame = response.data;

      setGames(prev => [...prev, {
        id: createdGame.id,
        name: createdGame.game_name,
        status: status,
        image_url: createdGame.screenshot,
        is_need_show_img: createdGame.is_need_show_img,
        pricing: {
          price_day: createdGame.pricing?.oneDay ?? 0,
          price_week: createdGame.pricing?.sevenDays ?? 0,
          price_month: createdGame.pricing?.thirtyOneDays ?? 0,
        }
      }]);

      toast({
        title: 'Game Created',
        description: `Game ${name} was created successfully`
      });

      setIsCreateModalOpen(false);
      setNewGame({
        name: '',
        status: 'Active',
        screenshot: '',
        pricing: { oneDay: 0, sevenDays: 0, thirtyOneDays: 0 },
      });
    } catch(e) {
      toast({
        title: 'Error',
        description: 'Failed to create game',
        variant: 'destructive',
      });
    } 
  };


  const handleUpdateVisibility = async(gameName: string, newStatus: boolean) => {
    try {
      await updateVisibility(gameName, newStatus);

      setGames(preveGames =>
        preveGames.map(game =>
          game.name === gameName
            ? { ...game, is_need_show_img: newStatus}
            : game
        )
      );

      toast({
        title: 'Visibility Updated',
        description: `Game ${gameName} is now ${newStatus ? 'visible (Active)' : 'hidden'}`,
      });
    } catch (e) {
      toast({
        title: 'Update Failed',
        description: `Failed to change visibility for game ${gameName}`,
        variant: 'destructive'
      });
    }
  };

  const handleEditGame = (game: Game) => {
    setEditingGame(game);
    setEditGame({
      name: game.name,
      status: game.status,
      screenshot: game.image_url,
      pricing: {
        oneDay: game.pricing.price_day,
        sevenDays: game.pricing.price_week,
        thirtyOneDays: game.pricing.price_month,
      },
    });
    setIsEditModalOpen(true);
  };

  const handleUpdateGame = async() => {
    if (!editingGame) return;

    try {
      const { name, screenshot, pricing, status } = editGame;

      if (!name.trim() || !screenshot) {
        toast({
          title: 'Validation Error',
          description: 'Game name and screenshot are required',
          variant: 'destructive',
        });
        return;
      }

      const pricingData = {
        day: pricing.oneDay,
        week: pricing.sevenDays,
        month: pricing.thirtyOneDays
      };

      await updateGame(
        editingGame.name,
        name.trim(),
        pricingData,
        screenshot.trim(),
        status
      );

      setGames(prev => prev.map(game => 
        game.id === editingGame.id 
          ? {
              ...game,
              name: name.trim(),
              status: status,
              image_url: screenshot.trim(),
              pricing: {
                price_day: pricing.oneDay,
                price_week: pricing.sevenDays,
                price_month: pricing.thirtyOneDays,
              }
            }
          : game
      ));

      toast({
        title: 'Game Updated',
        description: `Game ${name} was updated successfully`
      });

      setIsEditModalOpen(false);
      setEditingGame(null);
      setEditGame({
        name: '',
        status: 'Safe',
        screenshot: '',
        pricing: { oneDay: 0, sevenDays: 0, thirtyOneDays: 0 },
      });
    } catch(e) {
      toast({
        title: 'Error',
        description: 'Failed to update game',
        variant: 'destructive',
      });
    }
  };

  const handleDeleteGame = async(name: string) => {
    try {
      await deleteGame(name);
      setGames(prev => prev.filter(game => game.name !== name));
      toast({
        title: 'Deleted successfully',
        description: `Game ${name} deleted successfully`
      });
    } catch (e) {
      toast({
        title: 'Server Error',
        description: 'Failed to delete game',
        variant: 'destructive'
      });
    };
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold tracking-tight">Game Management</h1>
        <Dialog open={isCreateModalOpen} onOpenChange={setIsCreateModalOpen}>
          <DialogTrigger asChild>
            <Button>Add New Game</Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Create New Game</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Game Name</Label>
                  <Input
                    id="name"
                    value={newGame.name}
                    onChange={(e) => setNewGame({...newGame, name: e.target.value})}
                    placeholder="Enter game name"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="status">Status</Label>
                  <Select value={newGame.status} onValueChange={(value: 'Safe' | 'Updating') => setNewGame({...newGame, status: value})}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Safe">Safe</SelectItem>
                      <SelectItem value="Updating">Updating</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              
              <div className="space-y-2">
                <Label>Screenshot</Label>
                {newGame.screenshot ? (
                  <div className="relative">
                    <img src={newGame.screenshot} alt="Preview" className="w-full h-32 object-cover rounded border" />
                    <Button
                      variant="destructive" size="icon"
                      className="absolute top-1 right-1 h-6 w-6"
                      onClick={() => setNewGame({...newGame, screenshot: DEFAULT_IMAGE})}
                    >
                      <X className="h-3 w-3" />
                    </Button>
                  </div>
                ) : (
                  <label className="flex flex-col items-center justify-center h-32 border-2 border-dashed rounded cursor-pointer hover:bg-accent/50 transition-colors">
                    <Upload className="h-6 w-6 text-muted-foreground mb-1" />
                    <span className="text-sm text-muted-foreground">
                      {uploading ? 'Uploading...' : 'Click to upload'}
                    </span>
                    <input
                      type="file"
                      accept="image/png,image/jpeg,image/webp,image/gif"
                      className="hidden"
                      disabled={uploading}
                      onChange={async (e) => {
                        const file = e.target.files?.[0];
                        if (!file) return;
                        const url = await handleUpload(file);
                        if (url) setNewGame({...newGame, screenshot: url});
                        e.target.value = '';
                      }}
                    />
                  </label>
                )}
              </div>

              <div className="space-y-2">
                <Label>Pricing</Label>
                <div className="grid grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="oneDay">1 Day ($)</Label>
                    <Input
                      id="oneDay"
                      type="number"
                      value={newGame.pricing.oneDay}
                      onChange={(e) => setNewGame({
                        ...newGame, 
                        pricing: {...newGame.pricing, oneDay: Number(e.target.value)}
                      })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="sevenDays">7 Days ($)</Label>
                    <Input
                      id="sevenDays"
                      type="number"
                      value={newGame.pricing.sevenDays}
                      onChange={(e) => setNewGame({
                        ...newGame, 
                        pricing: {...newGame.pricing, sevenDays: Number(e.target.value)}
                      })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="thirtyOneDays">30 Days ($)</Label>
                    <Input
                      id="thirtyOneDays"
                      type="number"
                      value={newGame.pricing.thirtyOneDays}
                      onChange={(e) => setNewGame({
                        ...newGame, 
                        pricing: {...newGame.pricing, thirtyOneDays: Number(e.target.value)}
                      })}
                    />
                  </div>
                </div>
              </div>

              <div className="flex justify-end space-x-2">
                <Button variant="outline" onClick={() => setIsCreateModalOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleCreateGame}>
                  Create Game
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <Dialog open={isEditModalOpen} onOpenChange={setIsEditModalOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Edit Game</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="edit-name">Game Name</Label>
                <Input
                  id="edit-name"
                  value={editGame.name}
                  onChange={(e) => setEditGame({...editGame, name: e.target.value})}
                  placeholder="Enter game name"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="edit-status">Status</Label>
                <Select value={editGame.status} onValueChange={(value: 'Safe' | 'Updating') => setEditGame({...editGame, status: value})}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Safe">Safe</SelectItem>
                    <SelectItem value="Updating">Updating</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            
            <div className="space-y-2">
              <Label>Screenshot</Label>
              {editGame.screenshot ? (
                <div className="relative">
                  <img src={editGame.screenshot} alt="Preview" className="w-full h-32 object-cover rounded border" />
                  <Button
                    variant="destructive" size="icon"
                    className="absolute top-1 right-1 h-6 w-6"
                    onClick={() => setEditGame({...editGame, screenshot: DEFAULT_IMAGE})}
                  >
                    <X className="h-3 w-3" />
                  </Button>
                </div>
              ) : (
                <label className="flex flex-col items-center justify-center h-32 border-2 border-dashed rounded cursor-pointer hover:bg-accent/50 transition-colors">
                  <Upload className="h-6 w-6 text-muted-foreground mb-1" />
                  <span className="text-sm text-muted-foreground">
                    {uploading ? 'Uploading...' : 'Click to upload'}
                  </span>
                  <input
                    type="file"
                    accept="image/png,image/jpeg,image/webp,image/gif"
                    className="hidden"
                    disabled={uploading}
                    onChange={async (e) => {
                      const file = e.target.files?.[0];
                      if (!file) return;
                      const url = await handleUpload(file);
                      if (url) setEditGame({...editGame, screenshot: url});
                      e.target.value = '';
                    }}
                  />
                </label>
              )}
            </div>

            <div className="space-y-2">
              <Label>Pricing</Label>
              <div className="grid grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="edit-oneDay">1 Day ($)</Label>
                  <Input
                    id="edit-oneDay"
                    type="number"
                    value={editGame.pricing.oneDay}
                    onChange={(e) => setEditGame({
                      ...editGame, 
                      pricing: {...editGame.pricing, oneDay: Number(e.target.value)}
                    })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="edit-sevenDays">7 Days ($)</Label>
                  <Input
                    id="edit-sevenDays"
                    type="number"
                    value={editGame.pricing.sevenDays}
                    onChange={(e) => setEditGame({
                      ...editGame, 
                      pricing: {...editGame.pricing, sevenDays: Number(e.target.value)}
                    })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="edit-thirtyOneDays">30 Days ($)</Label>
                  <Input
                    id="edit-thirtyOneDays"
                    type="number"
                    value={editGame.pricing.thirtyOneDays}
                    onChange={(e) => setEditGame({
                      ...editGame, 
                      pricing: {...editGame.pricing, thirtyOneDays: Number(e.target.value)}
                    })}
                  />
                </div>
              </div>
            </div>

            <div className="flex justify-end space-x-2">
              <Button variant="outline" onClick={() => setIsEditModalOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleUpdateGame}>
                Update Game
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {games.map((game) => (
          <Card key={game.id} className="overflow-hidden">
            <div className="aspect-video relative bg-black/50">
              <img
                src={game.image_url}
                alt={game.name}
                className="w-full h-full object-contain"
              />
              <Badge 
                className="absolute top-2 right-2"
                variant={game.status === 'Safe' ? 'green' : 'destructive'}
              >
                {game.status}
              </Badge>
            </div>
            
            <CardHeader>
              <CardTitle className="text-lg">{game.name} / {game.id}</CardTitle>
            </CardHeader>
            
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <h4 className="font-medium">Pricing</h4>
                <div className="grid grid-cols-3 gap-2 text-sm">
                  <div className="text-center p-2 bg-muted rounded">
                    <div className="font-medium">{game.pricing.price_day}$</div>
                    <div className="text-xs text-muted-foreground">1 Day</div>
                  </div>
                  <div className="text-center p-2 bg-muted rounded">
                    <div className="font-medium">{game.pricing.price_week}$</div>
                    <div className="text-xs text-muted-foreground">7 Days</div>
                  </div>
                  <div className="text-center p-2 bg-muted rounded">
                    <div className="font-medium">{game.pricing.price_month}$</div>
                    <div className="text-xs text-muted-foreground">30 Days</div>
                  </div>
                </div>
              </div>

              <div className="flex space-x-2">
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="flex-1"
                  onClick={() => handleEditGame(game)}
                >
                  <Edit className="h-4 w-4 mr-1" />
                  Edit
                </Button>
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={() => handleUpdateVisibility(
                    game.name, game.is_need_show_img ? false : true
                  )}
                >
                  {game.is_need_show_img ? 'Hide Image' : 'Show Image'}
                </Button>
                <Button 
                  variant="destructive" 
                  size="sm"
                  onClick={() => {
                    setGameToDelete(game);
                    setIsConfirmDeleteOpen(true);
                  }}
                >
                  Delete
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
      <Dialog open={isConfirmDeleteOpen} onOpenChange={setIsConfirmDeleteOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Confirm Deletion</DialogTitle>
          </DialogHeader>
          
          <div className='space-y-1'>
            <p>Are you sure you want to delete game <strong>{gameToDelete?.name}?</strong></p>
            <p>This action cannot be undone.</p>
          </div>
          
          <div className='flex justify-end space-x-2 mt-4'>
            <Button variant='outline' onClick={() => setIsConfirmDeleteOpen(false)}>
              Cancel
            </Button>
            <Button
              variant='destructive'
              onClick={() => {
                if (gameToDelete) {
                  handleDeleteGame(gameToDelete?.name);
                }
                setIsConfirmDeleteOpen(false);
              }}
            >
              Delete
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default GameManagement;
