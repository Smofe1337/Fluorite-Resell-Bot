
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { AlertCircle, Lock, User } from 'lucide-react';
import { authorization, tokenValidator } from '@/api';

interface LoginProps {
  onLogin: (username: string, password: string) => void;
}

const getCookie = (name: string): string | null => {
  const cookies = document.cookie.split(';').map(cookie => cookie.trim());
  for (const cookie of cookies) {
    if (cookie.startsWith(`${name}=`)) {
      return cookie.substring(name.length + 1);
    }
  }
  return null;
};

const Login = ({ onLogin }: LoginProps) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const authorizationViaToken = async() => {
      const token = getCookie('access_token');
      if (!token) return;

      setIsLoading(true);
      setError('');

      try {
        const response = await tokenValidator(token);
        const data = response.data;

        if (data?.Status === true) {
          onLogin(data.username, '');
        } else {
          setError('Session expired or token invalid');
        }
      } catch (e) {
        setError('Session check failed');
      } finally {
        setIsLoading(false);
      }
    };

    authorizationViaToken();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const response = await authorization(username, password);
      const data = response.data;

      if (data?.detail?.Status === false) {
        setError(data.detail.Message || 'Invalid username or password');
        return;
      }

      if (data?.Status === true) {
        if (data.token) {
          document.cookie = `access_token=${data.token}; path=/; max-age=86400; samesite=lax`;
        }
        onLogin(username, password);
        return;
      }

      setError('Unexpected server response');
    } catch (err: any) {
      if (err.response) {
        const status = err.response.status;

        if (status === 404) {
          setError('Invalid username or password'); 
        } else if (status === 401) {
          setError('Invalid username or password');
        } else {
          const msg =
            err.response.data?.detail?.Message ||
            err.response.data?.Message ||
            'Server error';
          setError(msg);
        }
      } else {
        setError('Could not connect to the server');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-background via-muted/20 to-accent/10 p-4">
      <div className="w-full max-w-md space-y-8">
        <div className="text-center space-y-2">
          <div className="mx-auto w-16 h-16 bg-primary rounded-full flex items-center justify-center mb-4">
            <Lock className="w-8 h-8 text-primary-foreground" />
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">Welcome back</h1>
        </div>

        <Card className="shadow-xl border-0 bg-card/80 backdrop-blur-sm">
          <CardHeader className="space-y-1 pb-4">
            <CardTitle className="text-xl font-semibold text-center">Sign in</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <form onSubmit={handleSubmit} className="space-y-5">
              {error && (
                <div className="flex items-center space-x-3 text-destructive-foreground bg-destructive/10 border border-destructive/20 p-4 rounded-lg">
                  <AlertCircle className="w-5 h-5 flex-shrink-0" />
                  <span className="text-sm font-medium">{error}</span>
                </div>
              )}
              
              <div className="space-y-3">
                <Label htmlFor="username" className="text-sm font-medium text-foreground">
                  Username
                </Label>
                <div className="relative">
                  <User className="absolute left-3 top-3 w-4 h-4 text-muted-foreground" />
                  <Input
                    id="username"
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="Enter your username"
                    className="pl-10 h-12 border-border/50 focus:border-primary/50 bg-background/50"
                    required
                  />
                </div>
              </div>
              
              <div className="space-y-3">
                <Label htmlFor="password" className="text-sm font-medium text-foreground">
                  Password
                </Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 w-4 h-4 text-muted-foreground" />
                  <Input
                    id="password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter your password"
                    className="pl-10 h-12 border-border/50 focus:border-primary/50 bg-background/50"
                    required
                  />
                </div>
              </div>
              
              <Button 
                type="submit" 
                className="w-full h-12 text-base font-semibold bg-primary hover:bg-primary/90 text-primary-foreground shadow-lg transition-all duration-200 hover:shadow-xl"
                disabled={isLoading}
              >
                {isLoading ? (
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />
                    <span>Signing in...</span>
                  </div>
                ) : (
                  'Sign In'
                )}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Login;
