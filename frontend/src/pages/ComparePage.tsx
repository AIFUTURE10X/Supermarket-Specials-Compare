/**
 * Compare Page - Price comparison across all stores
 *
 * Uses SpecialsV2 layout with Staples data to show multi-store prices.
 * Focus is on finding the best price for each product.
 */
import { useState, useCallback, useRef, useEffect, memo, useMemo } from 'react';
import { useStaplesInfinite, useStaplesCategories, type StaplesFilters } from '../api/hooks';
import { StapleCard } from '../components/StapleCard';
import type { StapleCategory } from '../types';

const STORES = [
  {
    slug: 'woolworths',
    name: 'Woolworths',
    color: 'bg-green-600 hover:bg-green-700',
    textColor: 'text-white',
    borderColor: 'border-green-600',
    inactiveColor: 'bg-green-50 text-green-700 hover:bg-green-100 border-green-200',
  },
  {
    slug: 'coles',
    name: 'Coles',
    color: 'bg-red-600 hover:bg-red-700',
    textColor: 'text-white',
    borderColor: 'border-red-600',
    inactiveColor: 'bg-red-50 text-red-700 hover:bg-red-100 border-red-200',
  },
  {
    slug: 'aldi',
    name: 'ALDI',
    color: 'bg-blue-600 hover:bg-blue-700',
    textColor: 'text-white',
    borderColor: 'border-blue-600',
    inactiveColor: 'bg-blue-50 text-blue-700 hover:bg-blue-100 border-blue-200',
  },
  {
    slug: 'iga',
    name: 'IGA',
    color: 'bg-orange-500 hover:bg-orange-600',
    textColor: 'text-white',
    borderColor: 'border-orange-500',
    inactiveColor: 'bg-orange-50 text-orange-700 hover:bg-orange-100 border-orange-200',
  },
] as const;

const SORT_OPTIONS = [
  { value: 'savings', label: 'Biggest Savings' },
  { value: 'price_low', label: 'Price: Low to High' },
  { value: 'price_high', label: 'Price: High to Low' },
  { value: 'name', label: 'Name A-Z' },
] as const;

// Store icon component with brand colors
function StoreIcon({ store }: { store: string }) {
  switch (store) {
    case 'woolworths':
      return (
        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
          <circle cx="12" cy="12" r="10" fill="#1e8e3e" />
          <text x="12" y="16" textAnchor="middle" fontSize="12" fill="white" fontWeight="bold">W</text>
        </svg>
      );
    case 'coles':
      return (
        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
          <circle cx="12" cy="12" r="10" fill="#e01a22" />
          <text x="12" y="16" textAnchor="middle" fontSize="12" fill="white" fontWeight="bold">C</text>
        </svg>
      );
    case 'aldi':
      return (
        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
          <circle cx="12" cy="12" r="10" fill="#00457c" />
          <text x="12" y="16" textAnchor="middle" fontSize="12" fill="white" fontWeight="bold">A</text>
        </svg>
      );
    case 'iga':
      return (
        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
          <circle cx="12" cy="12" r="10" fill="#f7941d" />
          <text x="12" y="16" textAnchor="middle" fontSize="11" fill="white" fontWeight="bold">I</text>
        </svg>
      );
    default:
      return null;
  }
}

// Category icons
const CATEGORY_ICONS: Record<string, string> = {
  'fruit': '🍎',
  'vegetables': '🥕',
  'meat': '🍗',
  'seafood': '🐟',
  'dairy': '🥛',
  'bakery': '🍞',
  'deli': '🥓',
};

// Infinite scroll trigger
function LoadMoreTrigger({
  onLoadMore,
  hasMore,
  isLoading,
}: {
  onLoadMore: () => void;
  hasMore: boolean;
  isLoading: boolean;
}) {
  const triggerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!hasMore || isLoading) return;

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          onLoadMore();
        }
      },
      { rootMargin: '200px' }
    );

    if (triggerRef.current) {
      observer.observe(triggerRef.current);
    }

    return () => observer.disconnect();
  }, [hasMore, isLoading, onLoadMore]);

  if (!hasMore) return null;

  return (
    <div ref={triggerRef} className="flex justify-center py-8">
      {isLoading && (
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600" />
      )}
    </div>
  );
}

// Category sidebar component
const CategorySidebar = memo(function CategorySidebar({
  categories,
  selectedCategory,
  onSelectCategory,
}: {
  categories: StapleCategory[];
  selectedCategory: string | undefined;
  onSelectCategory: (slug: string | undefined) => void;
}) {
  return (
    <div className="bg-white rounded-xl border overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 border-b bg-gray-50">
        <h2 className="font-semibold text-gray-900">Categories</h2>
      </div>

      {/* All Products option */}
      <button
        onClick={() => onSelectCategory(undefined)}
        className={`w-full px-4 py-3 flex items-center gap-3 hover:bg-gray-50 transition-colors border-b border-gray-100 ${
          !selectedCategory ? 'bg-purple-50 border-l-4 border-l-purple-600' : ''
        }`}
      >
        <span className="text-2xl w-8 h-8 flex items-center justify-center flex-shrink-0">
          🏠
        </span>
        <span className={`flex-1 text-left text-sm ${!selectedCategory ? 'font-semibold text-purple-700' : 'text-gray-700'}`}>
          All Products
        </span>
        <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
      </button>

      {/* Category list */}
      <div className="max-h-[calc(100vh-300px)] overflow-y-auto">
        {categories.map((category) => {
          const isSelected = selectedCategory === category.slug;
          const icon = CATEGORY_ICONS[category.slug] || category.icon || '📦';

          return (
            <button
              key={category.slug}
              onClick={() => onSelectCategory(category.slug)}
              className={`w-full px-4 py-3 flex items-center gap-3 hover:bg-gray-50 transition-colors border-b border-gray-100 ${
                isSelected ? 'bg-purple-50 border-l-4 border-l-purple-600' : ''
              }`}
            >
              <span className="text-2xl w-8 h-8 flex items-center justify-center flex-shrink-0">
                {icon}
              </span>
              <span className={`flex-1 text-left text-sm ${isSelected ? 'font-semibold text-purple-700' : 'text-gray-700'}`}>
                {category.name}
              </span>
              <span className="text-xs text-gray-400 mr-2">
                ({category.count})
              </span>
              <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          );
        })}
      </div>
    </div>
  );
});

// Mobile category tabs
const CategoryTabs = memo(function CategoryTabs({
  categories,
  selectedCategory,
  onSelectCategory,
}: {
  categories: StapleCategory[];
  selectedCategory: string | undefined;
  onSelectCategory: (slug: string | undefined) => void;
}) {
  const scrollRef = useRef<HTMLDivElement>(null);

  return (
    <div className="relative">
      <div
        ref={scrollRef}
        className="flex gap-2 overflow-x-auto scrollbar-hide py-2 px-1"
        style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
      >
        {/* All Products tab */}
        <button
          onClick={() => onSelectCategory(undefined)}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-full font-medium text-sm transition-all whitespace-nowrap ${
            !selectedCategory
              ? 'bg-purple-600 text-white shadow-md'
              : 'bg-white text-gray-600 hover:bg-gray-100 border'
          }`}
        >
          <span className="text-base">🏠</span>
          <span>All</span>
        </button>

        {/* Category tabs */}
        {categories.map((category) => {
          const isSelected = selectedCategory === category.slug;
          const icon = CATEGORY_ICONS[category.slug] || category.icon || '📦';

          return (
            <button
              key={category.slug}
              onClick={() => onSelectCategory(category.slug)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-full font-medium text-sm transition-all whitespace-nowrap ${
                isSelected
                  ? 'bg-purple-600 text-white shadow-md'
                  : 'bg-white text-gray-600 hover:bg-gray-100 border'
              }`}
            >
              <span className="text-base">{icon}</span>
              <span>{category.name}</span>
              <span className={`text-xs ${isSelected ? 'text-purple-200' : 'text-gray-400'}`}>
                ({category.count})
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
});

export function ComparePage() {
  // Filters state
  const [selectedStore, setSelectedStore] = useState<string | undefined>(undefined);
  const [selectedCategory, setSelectedCategory] = useState<string | undefined>(undefined);
  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [sortBy, setSortBy] = useState<StaplesFilters['sort']>('savings');

  // Debounce search
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchQuery);
    }, 300);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Build filters object
  const filters: Omit<StaplesFilters, 'offset'> = useMemo(
    () => ({
      category: selectedCategory,
      store: selectedStore,
      sort: sortBy,
      search: debouncedSearch.length >= 2 ? debouncedSearch : undefined,
      limit: 50,
    }),
    [selectedCategory, selectedStore, sortBy, debouncedSearch]
  );

  // Fetch data
  const {
    data: staplesData,
    fetchNextPage,
    hasNextPage,
    isFetching,
    isFetchingNextPage,
    isLoading,
  } = useStaplesInfinite(filters);

  const { data: categoriesData } = useStaplesCategories();

  // Flatten pages into single array
  const products = useMemo(
    () => staplesData?.pages.flatMap((page) => page.products) ?? [],
    [staplesData]
  );

  const total = staplesData?.pages[0]?.total ?? 0;
  const totalProducts = categoriesData?.total_products ?? 0;

  // Calculate stats
  const avgSavings = useMemo(() => {
    if (products.length === 0) return 0;
    const totalSavings = products.reduce((sum, p) => sum + (p.savings_amount || 0), 0);
    return Math.round(totalSavings / products.length / 100);
  }, [products]);

  // Handlers
  const handleStoreClick = useCallback((slug: string | undefined) => {
    setSelectedStore(prev => prev === slug ? undefined : slug);
  }, []);

  const handleLoadMore = useCallback(() => {
    if (hasNextPage && !isFetchingNextPage) {
      fetchNextPage();
    }
  }, [hasNextPage, isFetchingNextPage, fetchNextPage]);

  const clearFilters = useCallback(() => {
    setSelectedStore(undefined);
    setSelectedCategory(undefined);
    setSearchQuery('');
    setSortBy('savings');
  }, []);

  const hasActiveFilters = selectedStore || selectedCategory || searchQuery;

  return (
    <div className="space-y-6">
      {/* Header with Stats + Page Navigation */}
      <div className="bg-gradient-to-r from-purple-600 to-indigo-700 rounded-2xl p-6 text-white">
        <h1 className="text-3xl font-bold mb-2">Price Showdown</h1>
        <p className="text-purple-100 mb-4">
          See who's cheapest, store by store
        </p>

        <div className="flex flex-wrap gap-4 text-sm items-center">
          {/* Page Navigation Buttons */}
          <a
            href="/"
            className="px-5 py-2 rounded-full font-semibold text-sm transition-all bg-orange-500 hover:bg-orange-400 text-white shadow-lg"
          >
            Specials
          </a>
          <a
            href="/staples"
            className="px-5 py-2 rounded-full font-semibold text-sm transition-all bg-emerald-500 hover:bg-emerald-400 text-white shadow-lg"
          >
            Staples
          </a>
          <a
            href="/compare"
            className="px-5 py-2 rounded-full font-semibold text-sm transition-all bg-pink-500 hover:bg-pink-400 text-white shadow-lg ring-2 ring-white"
          >
            Compare
          </a>

          <div className="bg-white/20 rounded-lg px-4 py-2">
            <span className="font-bold text-xl">{totalProducts}</span>
            <span className="ml-2">Products</span>
          </div>
          <div className="bg-white/20 rounded-lg px-4 py-2">
            <span className="font-bold text-xl">4</span>
            <span className="ml-2">Stores Compared</span>
          </div>
          {avgSavings > 0 && (
            <div className="bg-white/20 rounded-lg px-4 py-2">
              <span className="font-bold text-xl">${avgSavings}</span>
              <span className="ml-2">Avg Savings</span>
            </div>
          )}
        </div>
      </div>

      {/* Store Filters */}
      <div className="flex flex-wrap gap-2 items-center">
        <button
          onClick={() => handleStoreClick(undefined)}
          className={`px-4 py-2 rounded-full font-medium text-sm transition-all border ${
            !selectedStore
              ? 'bg-gray-800 text-white border-gray-800'
              : 'bg-gray-50 text-gray-600 hover:bg-gray-100 border-gray-200'
          }`}
        >
          All Stores
        </button>
        {STORES.map((store) => (
          <button
            key={store.slug}
            onClick={() => handleStoreClick(store.slug)}
            className={`px-4 py-2 rounded-full font-medium text-sm transition-all border flex items-center gap-1.5 ${
              selectedStore === store.slug
                ? `${store.color} ${store.textColor} ${store.borderColor}`
                : store.inactiveColor
            }`}
          >
            <StoreIcon store={store.slug} />
            {store.name}
          </button>
        ))}
      </div>

      {/* Mobile Category Tabs */}
      {categoriesData && (
        <div className="lg:hidden bg-white rounded-xl border p-2">
          <CategoryTabs
            categories={categoriesData.categories}
            selectedCategory={selectedCategory}
            onSelectCategory={setSelectedCategory}
          />
        </div>
      )}

      {/* Main Content with Sidebar Layout */}
      <div className="flex gap-6">
        {/* Category Sidebar - hidden on mobile, visible on desktop */}
        {categoriesData && (
          <div className="hidden lg:block w-72 flex-shrink-0">
            <div className="sticky top-4">
              <CategorySidebar
                categories={categoriesData.categories}
                selectedCategory={selectedCategory}
                onSelectCategory={setSelectedCategory}
              />
            </div>
          </div>
        )}

        {/* Main Content Area */}
        <div className="flex-1 min-w-0 space-y-4">
          {/* Filters Row */}
          <div className="bg-white rounded-xl border p-4">
            <div className="flex flex-wrap gap-4">
              {/* Search */}
              <div className="flex-1 min-w-[200px]">
                <div className="relative">
                  <input
                    type="text"
                    placeholder="Search products..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                  />
                  <svg
                    className="absolute left-3 top-2.5 h-5 w-5 text-gray-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                    />
                  </svg>
                </div>
              </div>

              {/* Sort */}
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as StaplesFilters['sort'])}
                className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 bg-white"
              >
                {SORT_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>

              {/* Clear Filters */}
              {hasActiveFilters && (
                <button
                  onClick={clearFilters}
                  className="px-4 py-2 text-sm text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors"
                >
                  Clear Filters
                </button>
              )}
            </div>
          </div>

          {/* Results Count */}
          <div className="flex justify-between items-center">
            <p className="text-gray-500">
              {isLoading
                ? 'Loading...'
                : `Showing ${products.length} of ${total} products`}
            </p>
            {isFetching && !isLoading && (
              <span className="text-sm text-purple-600">Updating...</span>
            )}
          </div>

          {/* Loading State */}
          {isLoading ? (
            <div className="flex items-center justify-center min-h-[400px]">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600" />
            </div>
          ) : products.length > 0 ? (
            <>
              {/* Products Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-4">
                {products.map((product, index) => (
                  <StapleCard
                    key={`${product.id}-${index}`}
                    product={product}
                  />
                ))}
              </div>

              {/* Infinite Scroll Trigger */}
              <LoadMoreTrigger
                onLoadMore={handleLoadMore}
                hasMore={!!hasNextPage}
                isLoading={isFetchingNextPage}
              />
            </>
          ) : (
            <div className="bg-white rounded-xl border p-12 text-center">
              <div className="text-5xl mb-4">🔍</div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                No products found
              </h3>
              <p className="text-gray-500 max-w-md mx-auto">
                {hasActiveFilters
                  ? 'No products match your filters. Try adjusting your search or clearing filters.'
                  : 'There are no products available at the moment.'}
              </p>
              {hasActiveFilters && (
                <button
                  onClick={clearFilters}
                  className="mt-4 px-6 py-2 bg-purple-600 text-white font-medium rounded-lg hover:bg-purple-700 transition-colors"
                >
                  Clear Filters
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
