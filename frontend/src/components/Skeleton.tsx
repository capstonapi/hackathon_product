export function Skeleton({ className = '' }: { className?: string }) {
  return <div className={`animate-pulse rounded-md bg-slate-200 ${className}`} />
}

export function ArticleCardSkeleton() {
  return (
    <div className="flex flex-col gap-3 rounded-lg border border-slate-200 bg-white p-4">
      <Skeleton className="h-4 w-20" />
      <Skeleton className="h-5 w-3/4" />
      <Skeleton className="h-4 w-full" />
      <Skeleton className="h-4 w-2/3" />
    </div>
  )
}

export function ArticleCardSkeletonGrid({ count = 6 }: { count?: number }) {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {Array.from({ length: count }).map((_, index) => (
        <ArticleCardSkeleton key={index} />
      ))}
    </div>
  )
}
