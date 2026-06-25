
import { useState, useEffect, useRef, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog';
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { startBroadcast, getBroadcastStatus, uploadImage } from '@/api';
import { useToast } from '@/hooks/use-toast';
import { Send, Upload, X, Plus, Image, Bold, Italic, Code, Strikethrough, Underline, Link2, ChevronUp, ChevronDown, Trash2 } from 'lucide-react';

const OPEN_TAG: Record<string, string> = {
  b: '<b>', strong: '<b>',
  i: '<i>', em: '<i>',
  u: '<u>', ins: '<u>',
  s: '<s>', strike: '<s>', del: '<s>',
  code: '<code>', pre: '<pre>',
};
const CLOSE_TAG: Record<string, string> = {
  b: '</b>', strong: '</b>',
  i: '</i>', em: '</i>',
  u: '</u>', ins: '</u>',
  s: '</s>', strike: '</s>', del: '</s>',
  code: '</code>', pre: '</pre>',
};

function normalizeHtml(html: string): string {
  const root = document.createElement('div');
  root.innerHTML = html;

  let out = '';

  function walk(node: Node) {
    node.childNodes.forEach((child) => {
      if (child.nodeType === Node.TEXT_NODE) {
        out += child.textContent || '';
        return;
      }
      if (child.nodeType !== Node.ELEMENT_NODE) return;

      const el = child as HTMLElement;
      const tag = el.tagName.toLowerCase();

      if (tag === 'br') {
        out += '\n';
        return;
      }

      if (tag === 'div' || tag === 'p') {
        if (out.length && !out.endsWith('\n')) out += '\n';
        walk(el);
        if (!out.endsWith('\n')) out += '\n';
        return;
      }

      if (tag === 'a') {
        out += `<a href="${el.getAttribute('href') || ''}">`;
        walk(el);
        out += '</a>';
        return;
      }

      if (OPEN_TAG[tag]) {
        out += OPEN_TAG[tag];
        walk(el);
        out += CLOSE_TAG[tag];
        return;
      }

      walk(el);
    });
  }

  walk(root);

  return out
    .replace(/[ \t]+\n/g, '\n')
    .replace(/\n{3,}/g, '\n\n')
    .trim();
}

interface InlineBtn {
  id: string;
  text: string;
  url: string;
}

function moveItem<T>(arr: T[], from: number, to: number): T[] {
  const copy = [...arr];
  const [item] = copy.splice(from, 1);
  copy.splice(to, 0, item);
  return copy;
}

const BroadcastManagement = () => {
  const { toast } = useToast();
  const editorRef = useRef<HTMLDivElement>(null);

  const [photo, setPhoto] = useState('');
  const [buttons, setButtons] = useState<InlineBtn[]>([]);
  const [uploading, setUploading] = useState(false);
  const [sending, setSending] = useState(false);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [isEmpty, setIsEmpty] = useState(true);

  const [linkDialogOpen, setLinkDialogOpen] = useState(false);
  const [linkUrl, setLinkUrl] = useState('');
  const savedRangeRef = useRef<Range | null>(null);

  const [status, setStatus] = useState<{
    running: boolean;
    finished: boolean;
    total?: number;
    sent?: number;
    failed?: number;
  } | null>(null);

  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const s = await getBroadcastStatus();
        if (s.running || s.finished) {
          setStatus(s);
          setSending(s.running);
        }
      } catch { void 0; }
    };
    checkStatus();
  }, []);

  useEffect(() => {
    if (sending) {
      pollRef.current = setInterval(async () => {
        try {
          const s = await getBroadcastStatus();
          setStatus(s);
          if (s.finished) {
            setSending(false);
            if (pollRef.current) clearInterval(pollRef.current);
          }
        } catch { void 0; }
      }, 2000);
    }
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, [sending]);

  const execFormat = useCallback((command: string, value?: string) => {
    editorRef.current?.focus();
    document.execCommand(command, false, value);
  }, []);

  const openLinkDialog = useCallback(() => {
    const selection = window.getSelection();
    if (!selection || selection.rangeCount === 0) {
      toast({ title: 'Place cursor in the text first', variant: 'destructive' });
      return;
    }
    savedRangeRef.current = selection.getRangeAt(0).cloneRange();
    setLinkUrl('');
    setLinkDialogOpen(true);
  }, [toast]);

  const applyLink = useCallback(() => {
    const url = linkUrl.trim();
    setLinkDialogOpen(false);
    if (!url) return;

    const range = savedRangeRef.current;
    if (!range) return;

    editorRef.current?.focus();
    const selection = window.getSelection();
    selection?.removeAllRanges();
    selection?.addRange(range);

    if (range.collapsed) {
      document.execCommand('insertHTML', false, `<a href="${url}">${url}</a>`);
    } else {
      document.execCommand('createLink', false, url);
    }
    savedRangeRef.current = null;
  }, [linkUrl]);

  const handleUpload = async (file: File) => {
    setUploading(true);
    try {
      const url = await uploadImage(file);
      setPhoto(url);
    } catch {
      toast({ title: 'Upload Failed', description: 'Failed to upload image', variant: 'destructive' });
    } finally {
      setUploading(false);
    }
  };

  const getEditorText = (): string => {
    if (!editorRef.current) return '';
    return normalizeHtml(editorRef.current.innerHTML);
  };

  const handleSend = async () => {
    setConfirmOpen(false);

    const messageText = getEditorText();
    if (!messageText.trim()) {
      toast({ title: 'Validation Error', description: 'Message text is required', variant: 'destructive' });
      return;
    }

    try {
      const validButtons = buttons
        .filter(b => b.text.trim() && b.url.trim())
        .map(b => ({ text: b.text.trim(), url: b.url.trim() }));

      const result = await startBroadcast(messageText, photo ? [photo] : [], validButtons);

      setSending(true);
      setStatus({ running: true, finished: false, total: result.total, sent: 0, failed: 0 });

      toast({ title: 'Broadcast Started', description: `Sending to ${result.total} users` });
    } catch (e: any) {
      const detail = e?.response?.data?.detail;
      toast({
        title: 'Error',
        description: detail || 'Failed to start broadcast',
        variant: 'destructive',
      });
    }
  };

  const handleReset = () => {
    if (editorRef.current) editorRef.current.innerHTML = '';
    setIsEmpty(true);
    setPhoto('');
    setButtons([]);
    setStatus(null);
  };

  const handleEditorInput = () => {
    const content = editorRef.current?.textContent || '';
    setIsEmpty(!content.trim());
  };

  const addButton = () => {
    setButtons(prev => [...prev, { id: crypto.randomUUID(), text: '', url: '' }]);
  };

  const updateButton = (id: string, field: 'text' | 'url', value: string) => {
    setButtons(prev => prev.map(b => b.id === id ? { ...b, [field]: value } : b));
  };

  const removeButton = (id: string) => {
    setButtons(prev => prev.filter(b => b.id !== id));
  };

  const progress = status && status.total
    ? Math.round(((status.sent || 0) + (status.failed || 0)) / status.total * 100)
    : 0;

  const toolbarButtons = [
    { icon: Bold, label: 'Bold', action: () => execFormat('bold') },
    { icon: Italic, label: 'Italic', action: () => execFormat('italic') },
    { icon: Underline, label: 'Underline', action: () => execFormat('underline') },
    { icon: Strikethrough, label: 'Strikethrough', action: () => execFormat('strikeThrough') },
    { icon: Code, label: 'Code', action: () => {
      const selection = window.getSelection();
      if (!selection || selection.rangeCount === 0) return;
      const range = selection.getRangeAt(0);
      const code = document.createElement('code');
      code.style.backgroundColor = 'rgba(127,127,127,0.15)';
      code.style.padding = '1px 4px';
      code.style.borderRadius = '3px';
      code.style.fontFamily = 'monospace';
      range.surroundContents(code);
      selection.collapseToEnd();
    }},
    { icon: Link2, label: 'Link', action: openLinkDialog },
  ];

  return (
    <div className="space-y-6 max-w-3xl">
      <h1 className="text-2xl font-bold">Broadcast</h1>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Compose Message</CardTitle>
        </CardHeader>
        <CardContent className="space-y-5">

          <div className="space-y-2">
            <Label>Message Text</Label>
            <div className="border rounded-md overflow-hidden">
              <div className="flex items-center gap-1 p-2 border-b bg-muted/50">
                {toolbarButtons.map((btn) => (
                  <Button
                    key={btn.label}
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8"
                    title={btn.label}
                    onMouseDown={(e) => e.preventDefault()}
                    onClick={btn.action}
                  >
                    <btn.icon className="h-4 w-4" />
                  </Button>
                ))}
              </div>
              <div
                ref={editorRef}
                contentEditable
                onInput={handleEditorInput}
                data-placeholder="Type your message here..."
                className="min-h-[150px] px-3 py-2 text-sm focus:outline-none empty:before:content-[attr(data-placeholder)] empty:before:text-muted-foreground empty:before:pointer-events-none"
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label className="flex items-center gap-2">
              <Image className="h-4 w-4" />
              Photo (optional)
            </Label>

            {photo ? (
              <div className="relative inline-block">
                <img src={photo} alt="Preview" className="max-h-48 rounded border object-cover" />
                <Button
                  variant="destructive"
                  size="icon"
                  className="absolute top-1 right-1 h-6 w-6"
                  onClick={() => setPhoto('')}
                >
                  <X className="h-3 w-3" />
                </Button>
              </div>
            ) : (
              <label className="flex flex-col items-center justify-center h-32 border-2 border-dashed rounded-md cursor-pointer hover:bg-accent/50 transition-colors">
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
                    await handleUpload(file);
                    e.target.value = '';
                  }}
                />
              </label>
            )}
          </div>

          <div className="space-y-3">
            {buttons.length > 0 && (
              <div className="space-y-2">
                {buttons.map((btn, i) => (
                  <div key={btn.id} className="flex items-start gap-2 p-3 border rounded-md bg-muted/30">
                    <div className="flex-1 grid grid-cols-2 gap-2">
                      <Input
                        value={btn.text}
                        onChange={(e) => updateButton(btn.id, 'text', e.target.value)}
                        placeholder="Button text"
                        className="h-9 text-sm"
                      />
                      <Input
                        value={btn.url}
                        onChange={(e) => updateButton(btn.id, 'url', e.target.value)}
                        placeholder="https://..."
                        className="h-9 text-sm"
                      />
                    </div>
                    <div className="flex items-center gap-1 flex-shrink-0 pt-0.5">
                      <Button
                        variant="ghost" size="icon" className="h-7 w-7"
                        disabled={i === 0}
                        onClick={() => setButtons(moveItem(buttons, i, i - 1))}
                      >
                        <ChevronUp className="h-3.5 w-3.5" />
                      </Button>
                      <Button
                        variant="ghost" size="icon" className="h-7 w-7"
                        disabled={i === buttons.length - 1}
                        onClick={() => setButtons(moveItem(buttons, i, i + 1))}
                      >
                        <ChevronDown className="h-3.5 w-3.5" />
                      </Button>
                      <Button
                        variant="ghost" size="icon" className="h-7 w-7 text-destructive hover:text-destructive"
                        onClick={() => removeButton(btn.id)}
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}

            <Button variant="outline" size="sm" onClick={addButton} className="gap-1.5">
              <Plus className="h-3.5 w-3.5" />
              Add Button
            </Button>
          </div>

          <div className="flex gap-3 pt-2">
            <Button
              onClick={() => setConfirmOpen(true)}
              disabled={isEmpty || sending}
            >
              <Send className="h-4 w-4 mr-2" />
              Send Broadcast
            </Button>
            <Button variant="outline" onClick={handleReset} disabled={sending}>
              Reset
            </Button>
          </div>
        </CardContent>
      </Card>

      {status && (status.running || status.finished) && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">
              {status.running ? 'Sending...' : 'Broadcast Complete'}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex justify-between text-sm">
              <span>
                Sent: <span className="font-semibold text-green-500">{status.sent || 0}</span>
              </span>
              <span>
                Failed: <span className="font-semibold text-red-500">{status.failed || 0}</span>
              </span>
              <span>
                Total: <span className="font-semibold">{status.total || 0}</span>
              </span>
            </div>
            <div className="w-full bg-secondary rounded-full h-3 overflow-hidden">
              <div
                className="bg-primary h-full rounded-full transition-all duration-500"
                style={{ width: `${progress}%` }}
              />
            </div>
            <p className="text-sm text-muted-foreground text-center">{progress}%</p>
          </CardContent>
        </Card>
      )}

      <AlertDialog open={confirmOpen} onOpenChange={setConfirmOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Send Broadcast?</AlertDialogTitle>
            <AlertDialogDescription>
              This will send the message to all active users. This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleSend}>Send</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      <Dialog open={linkDialogOpen} onOpenChange={setLinkDialogOpen}>
        <DialogContent className="max-w-sm">
          <DialogHeader>
            <DialogTitle>Insert Link</DialogTitle>
          </DialogHeader>
          <div className="space-y-2">
            <Label>URL</Label>
            <Input
              autoFocus
              value={linkUrl}
              onChange={(e) => setLinkUrl(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault();
                  applyLink();
                }
              }}
              placeholder="https://example.com"
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setLinkDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={applyLink} disabled={!linkUrl.trim()}>
              Insert
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default BroadcastManagement;
