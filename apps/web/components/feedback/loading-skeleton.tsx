export function LoadingSkeleton() {
  return (
    <div className="loading-skeleton" role="status" aria-live="polite">
      <span>Loading opportunities</span>
      {[1, 2, 3].map((item) => (
        <div key={item} />
      ))}
    </div>
  );
}
