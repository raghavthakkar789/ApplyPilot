"use client";

import { Search, SlidersHorizontal } from "lucide-react";
import { useState } from "react";
import type { DiscoverFilters } from "@/features/discover/discover-types";

interface Props {
  filters: DiscoverFilters;
  onChange: (next: DiscoverFilters) => void;
  sort: string;
  onSort: (value: string) => void;
  activeCount: number;
}

export function OpportunityToolbar({
  filters,
  onChange,
  sort,
  onSort,
  activeCount,
}: Props) {
  const [mobileFiltersOpen, setMobileFiltersOpen] = useState(false);
  const update = (key: keyof DiscoverFilters, value: string) =>
    onChange({ ...filters, [key]: value });
  return (
    <section className="toolbar" aria-label="Opportunity search and filters">
      <label className="search-field">
        <Search aria-hidden="true" size={18} />
        <span className="sr-only">Search opportunities</span>
        <input
          value={filters.query}
          onChange={(e) => update("query", e.target.value)}
          placeholder="Search roles, skills, employers"
        />
      </label>
      <div
        id="opportunity-filter-controls"
        className="filter-row"
        data-mobile-open={mobileFiltersOpen}
      >
        <Filter
          label="Role"
          value={filters.role}
          values={["Platform Engineer", "Backend Engineer", "Cloud Engineer"]}
          onChange={(v) => update("role", v)}
        />
        <Filter
          label="Skills"
          value={filters.skill}
          values={["Python", "PostgreSQL", "Docker", "TypeScript"]}
          onChange={(v) => update("skill", v)}
        />
        <Filter
          label="Location"
          value={filters.location}
          values={["India", "Remote", "Germany"]}
          onChange={(v) => update("location", v)}
        />
        <Filter
          label="Source"
          value={filters.source}
          values={["Greenhouse", "Lever", "Ashby", "Remotive"]}
          onChange={(v) => update("source", v)}
        />
        <button
          className="advanced-button"
          type="button"
          aria-label={`${activeCount} advanced filters applied`}
          aria-expanded={mobileFiltersOpen}
          aria-controls="opportunity-filter-controls"
          onClick={() => setMobileFiltersOpen((open) => !open)}
        >
          <SlidersHorizontal aria-hidden="true" size={16} />
          Advanced <span>{activeCount}</span>
        </button>
        <label className="sort-control">
          <span>Sort</span>
          <select
            aria-label="Sort opportunities"
            value={sort}
            onChange={(e) => onSort(e.target.value)}
          >
            <option value="ranking">Ranking derivation</option>
            <option value="newest">Newest</option>
            <option value="capability">Capability alignment</option>
          </select>
        </label>
      </div>
    </section>
  );
}

function Filter({
  label,
  value,
  values,
  onChange,
}: {
  label: string;
  value: string;
  values: string[];
  onChange: (value: string) => void;
}) {
  return (
    <label className="filter">
      <span className="sr-only">{label} filter</span>
      <select
        aria-label={`${label} filter`}
        value={value}
        onChange={(e) => onChange(e.target.value)}
      >
        <option value="">{label}</option>
        {values.map((item) => (
          <option key={item}>{item}</option>
        ))}
      </select>
    </label>
  );
}
