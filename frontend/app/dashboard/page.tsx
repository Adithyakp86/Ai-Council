'use client';

import { useState, useEffect } from 'react';
import { useAuthStore } from '@/lib/auth-store';
import { ProtectedRoute } from '@/components/auth/protected-route';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api-client';
import { useToast } from '@/hooks/use-toast';
import {
  Activity,
  DollarSign,
  TrendingUp,
  Zap,
  BarChart3,
  Clock,
  Target,
} from 'lucide-react';

interface DashboardStats {
  totalRequests: number;
  totalCost: number;
  averageConfidence: number;
  requestsByMode: Record<string, number>;
  requestsOverTime: Array<{ date: string; count: number }>;
  topModels: Array<{ modelId: string; count: number; avgCost: number }>;
  averageResponseTime: number;
}

function DashboardContent() {
  const router = useRouter();
  const { user, logout } = useAuthStore();
  const { toast } = useToast();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get<DashboardStats>('/api/v1/user/stats');
      setStats(response.data);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to load dashboard statistics',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    router.push('/');
  };

  const getModeIcon = (mode: string) => {
    switch (mode) {
      case 'fast':
        return '⚡';
      case 'balanced':
        return '⚖️';
      case 'best_quality':
        return '💎';
      default:
        return '📋';
    }
  };

  return (
    <div className="min-h-screen bg-background py-8 px-4">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-3xl font-bold">Dashboard</h1>
            <p className="text-muted-foreground">Welcome back, {user?.name}!</p>
          </div>
          <div className="flex gap-2">
            <Button onClick={() => router.push('/query')}>
              New Query
            </Button>
            <Button variant="outline" onClick={() => router.push('/history')}>
              History
            </Button>
            <Button variant="outline" onClick={() => router.push('/profile')}>
              Profile
            </Button>
            <Button variant="outline" onClick={handleLogout}>
              Logout
            </Button>
          </div>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[...Array(4)].map((_, i) => (
              <Card key={i} className="animate-pulse">
                <CardHeader className="pb-2">
                  <div className="h-4 bg-muted rounded w-1/2 mb-2" />
                </CardHeader>
                <CardContent>
                  <div className="h-8 bg-muted rounded w-3/4" />
                </CardContent>
              </Card>
            ))}
          </div>
        ) : stats ? (
          <>
            {/* Overview Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {/* Total Requests */}
              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium">Total Requests</CardTitle>
                  <Activity className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats.totalRequests}</div>
                  <p className="text-xs text-muted-foreground mt-1">
                    All time submissions
                  </p>
                </CardContent>
              </Card>

              {/* Total Cost */}
              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium">Total Cost</CardTitle>
                  <DollarSign className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">${stats.totalCost.toFixed(2)}</div>
                  <p className="text-xs text-muted-foreground mt-1">
                    Across all requests
                  </p>
                </CardContent>
              </Card>

              {/* Average Confidence */}
              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium">Avg Confidence</CardTitle>
                  <Target className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {(stats.averageConfidence * 100).toFixed(0)}%
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    Response quality
                  </p>
                </CardContent>
              </Card>

              {/* Average Response Time */}
              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium">Avg Response Time</CardTitle>
                  <Clock className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {stats.averageResponseTime.toFixed(1)}s
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    Processing speed
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Requests by Mode */}
              <Card>
                <CardHeader>
                  <CardTitle>Requests by Execution Mode</CardTitle>
                  <CardDescription>
                    Distribution of your query execution preferences
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {Object.entries(stats.requestsByMode).map(([mode, count]) => {
                      const total = Object.values(stats.requestsByMode).reduce(
                        (sum, c) => sum + c,
                        0
                      );
                      const percentage = total > 0 ? (count / total) * 100 : 0;
                      return (
                        <div key={mode}>
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-2">
                              <span className="text-lg">{getModeIcon(mode)}</span>
                              <span className="text-sm font-medium capitalize">
                                {mode.replace('_', ' ')}
                              </span>
                            </div>
                            <span className="text-sm text-muted-foreground">
                              {count} ({percentage.toFixed(0)}%)
                            </span>
                          </div>
                          <div className="h-2 bg-muted rounded-full overflow-hidden">
                            <div
                              className="h-full bg-primary transition-all"
                              style={{ width: `${percentage}%` }}
                            />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>

              {/* Top Models */}
              <Card>
                <CardHeader>
                  <CardTitle>Most Used Models</CardTitle>
                  <CardDescription>
                    AI models that processed your requests
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {stats.topModels.slice(0, 5).map((model, index) => (
                      <div key={index} className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-sm font-medium text-primary">
                            {index + 1}
                          </div>
                          <div>
                            <div className="text-sm font-medium">{model.modelId}</div>
                            <div className="text-xs text-muted-foreground">
                              {model.count} request{model.count !== 1 ? 's' : ''}
                            </div>
                          </div>
                        </div>
                        <div className="text-sm text-muted-foreground">
                          ${model.avgCost.toFixed(4)} avg
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Requests Over Time */}
            <Card>
              <CardHeader>
                <CardTitle>Request Activity</CardTitle>
                <CardDescription>
                  Your query submissions over the last 30 days
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[200px] flex items-end justify-between gap-2">
                  {stats.requestsOverTime.slice(-30).map((item, index) => {
                    const maxCount = Math.max(
                      ...stats.requestsOverTime.map((i) => i.count),
                      1
                    );
                    const height = (item.count / maxCount) * 100;
                    return (
                      <div
                        key={index}
                        className="flex-1 bg-primary/20 hover:bg-primary/40 rounded-t transition-all cursor-pointer group relative"
                        style={{ height: `${height}%`, minHeight: item.count > 0 ? '4px' : '0' }}
                        title={`${new Date(item.date).toLocaleDateString()}: ${item.count} requests`}
                      >
                        <div className="absolute bottom-full mb-2 left-1/2 transform -translate-x-1/2 bg-popover text-popover-foreground px-2 py-1 rounded text-xs whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
                          {new Date(item.date).toLocaleDateString()}: {item.count}
                        </div>
                      </div>
                    );
                  })}
                </div>
                <div className="flex justify-between text-xs text-muted-foreground mt-4">
                  <span>30 days ago</span>
                  <span>Today</span>
                </div>
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Button
                    variant="outline"
                    className="h-auto py-4 flex flex-col items-center gap-2"
                    onClick={() => router.push('/query')}
                  >
                    <Zap className="h-6 w-6" />
                    <span>New Query</span>
                  </Button>
                  <Button
                    variant="outline"
                    className="h-auto py-4 flex flex-col items-center gap-2"
                    onClick={() => router.push('/history')}
                  >
                    <BarChart3 className="h-6 w-6" />
                    <span>View History</span>
                  </Button>
                  <Button
                    variant="outline"
                    className="h-auto py-4 flex flex-col items-center gap-2"
                    onClick={fetchStats}
                  >
                    <TrendingUp className="h-6 w-6" />
                    <span>Refresh Stats</span>
                  </Button>
                </div>
              </CardContent>
            </Card>
          </>
        ) : (
          <Card>
            <CardContent className="p-12 text-center">
              <div className="text-4xl mb-4">📊</div>
              <h3 className="text-lg font-medium mb-2">No data yet</h3>
              <p className="text-muted-foreground mb-4">
                Submit your first query to see statistics
              </p>
              <Button onClick={() => router.push('/query')}>
                Get Started
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <DashboardContent />
    </ProtectedRoute>
  );
}
