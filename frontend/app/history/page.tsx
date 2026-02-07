'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { councilApi } from '@/lib/council-api';
import { ProtectedRoute } from '@/components/auth/protected-route';
import { Search, ChevronLeft, ChevronRight, Calendar, Filter } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

interface HistoryItem {
  id: string;
  content: string;
  executionMode: string;
  status: 'pending' | 'completed' | 'failed';
  createdAt: string;
  cost?: number;
  confidence?: number;
}

export default function HistoryPage() {
  const router = useRouter();
  const { toast } = useToast();
  const [items, setItems] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState('');
  const [modeFilter, setModeFilter] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  const limit = 20;

  useEffect(() => {
    fetchHistory();
  }, [page, search, modeFilter, startDate, endDate]);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const response = await councilApi.getHistory({
        page,
        limit,
        search: search || undefined,
        mode: modeFilter || undefined,
        startDate: startDate || undefined,
        endDate: endDate || undefined,
      });
      setItems(response.items);
      setTotal(response.total);
      setTotalPages(response.pages);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to load request history',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (value: string) => {
    setSearch(value);
    setPage(1);
  };

  const handleModeFilter = (mode: string) => {
    setModeFilter(mode === modeFilter ? '' : mode);
    setPage(1);
  };

  const handleViewDetails = (requestId: string) => {
    router.push(`/request/${requestId}`);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800 dark:bg-green-950 dark:text-green-300';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-950 dark:text-yellow-300';
      case 'failed':
        return 'bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-300';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-950 dark:text-gray-300';
    }
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
    <ProtectedRoute>
      <div className="container mx-auto py-8 px-4 max-w-7xl">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Request History</h1>
          <p className="text-muted-foreground">
            View and manage your past AI Council requests
          </p>
        </div>

        {/* Filters */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-lg">Filters</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by content..."
                value={search}
                onChange={(e) => handleSearch(e.target.value)}
                className="pl-10"
              />
            </div>

            {/* Mode Filter */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Execution Mode</label>
              <div className="flex flex-wrap gap-2">
                {['fast', 'balanced', 'best_quality'].map((mode) => (
                  <Button
                    key={mode}
                    variant={modeFilter === mode ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => handleModeFilter(mode)}
                  >
                    {getModeIcon(mode)} {mode.replace('_', ' ')}
                  </Button>
                ))}
              </div>
            </div>

            {/* Date Range */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Start Date</label>
                <Input
                  type="date"
                  value={startDate}
                  onChange={(e) => {
                    setStartDate(e.target.value);
                    setPage(1);
                  }}
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">End Date</label>
                <Input
                  type="date"
                  value={endDate}
                  onChange={(e) => {
                    setEndDate(e.target.value);
                    setPage(1);
                  }}
                />
              </div>
            </div>

            {/* Clear Filters */}
            {(search || modeFilter || startDate || endDate) && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  setSearch('');
                  setModeFilter('');
                  setStartDate('');
                  setEndDate('');
                  setPage(1);
                }}
              >
                Clear All Filters
              </Button>
            )}
          </CardContent>
        </Card>

        {/* Results Summary */}
        <div className="mb-4 text-sm text-muted-foreground">
          Showing {items.length} of {total} request{total !== 1 ? 's' : ''}
        </div>

        {/* History List */}
        {loading ? (
          <div className="space-y-4">
            {[...Array(5)].map((_, i) => (
              <Card key={i} className="animate-pulse">
                <CardContent className="p-6">
                  <div className="h-4 bg-muted rounded w-3/4 mb-2" />
                  <div className="h-3 bg-muted rounded w-1/2" />
                </CardContent>
              </Card>
            ))}
          </div>
        ) : items.length === 0 ? (
          <Card>
            <CardContent className="p-12 text-center">
              <div className="text-4xl mb-4">📭</div>
              <h3 className="text-lg font-medium mb-2">No requests found</h3>
              <p className="text-muted-foreground mb-4">
                {search || modeFilter || startDate || endDate
                  ? 'Try adjusting your filters'
                  : 'Submit your first query to get started'}
              </p>
              <Button onClick={() => router.push('/dashboard')}>
                Go to Dashboard
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {items.map((item) => (
              <Card
                key={item.id}
                className="hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => handleViewDetails(item.id)}
              >
                <CardContent className="p-6">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      {/* Content Preview */}
                      <p className="text-sm font-medium mb-2 line-clamp-2">
                        {item.content}
                      </p>

                      {/* Metadata */}
                      <div className="flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
                        <span className="flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          {formatDate(item.createdAt)}
                        </span>
                        <span className="flex items-center gap-1">
                          {getModeIcon(item.executionMode)}
                          {item.executionMode.replace('_', ' ')}
                        </span>
                        {item.cost !== undefined && (
                          <span>${item.cost.toFixed(4)}</span>
                        )}
                        {item.confidence !== undefined && (
                          <span>{(item.confidence * 100).toFixed(0)}% confidence</span>
                        )}
                      </div>
                    </div>

                    {/* Status Badge */}
                    <div>
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(
                          item.status
                        )}`}
                      >
                        {item.status}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="mt-6 flex items-center justify-between">
            <div className="text-sm text-muted-foreground">
              Page {page} of {totalPages}
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
              >
                <ChevronLeft className="h-4 w-4 mr-1" />
                Previous
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
              >
                Next
                <ChevronRight className="h-4 w-4 ml-1" />
              </Button>
            </div>
          </div>
        )}
      </div>
    </ProtectedRoute>
  );
}
