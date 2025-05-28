// app/components/VirtualizedMultiSelect.tsx
"use client";

import React, { useState, useMemo } from "react";
import { FixedSizeList as List } from "react-window";
import AutoSizer from "react-virtualized-auto-sizer";
import debounce from "lodash.debounce";

type Option = string;

type Props = {
  label?: string;
  options: Option[];
  selected: Option[];
  onChange: (selected: Option[]) => void;
  placeholder?: string;
  height?: number;
  itemHeight?: number;
  /** if true, the built-in filter input is hidden */
  hideSearchInput?: boolean;
  /** your parent can pass bg-gray-800, rounded-lg, borders, etc */
  className?: string;
};

export default function VirtualizedMultiSelect({
  label,
  options,
  selected = [],
  onChange,
  placeholder = "Search…",
  height = 200,
  itemHeight = 36,
  hideSearchInput = false,
  className = "",
}: Props) {
  const [filter, setFilter] = useState("");

  const filteredOptions = useMemo(
    () =>
      options.filter((opt) =>
        opt.toLowerCase().includes(filter.toLowerCase())
      ),
    [options, filter]
  );

  const debouncedFilter = useMemo(
    () => debounce((val: string) => setFilter(val), 200),
    []
  );

  const toggleOption = (value: string) => {
    if (selected.includes(value)) {
      onChange(selected.filter((v) => v !== value));
    } else {
      onChange([...selected, value]);
    }
  };

  const Row = ({
    index,
    style,
  }: {
    index: number;
    style: React.CSSProperties;
  }) => {
    const value = filteredOptions[index];
    const isChecked = selected.includes(value);
    return (
      <div
        style={style}
        className="px-3 py-2 cursor-pointer flex items-center hover:bg-gray-100"
        onClick={() => toggleOption(value)}
      >
        <input
          type="checkbox"
          checked={isChecked}
          onChange={() => {}}
          onClick={(e) => e.stopPropagation()}
          className="mr-2 h-4 w-4 text-indigo-500"
        />
        <span className="truncate">{value}</span>
      </div>
    );
  };

  return (
    <div className={className + " space-y-1"}>
      {label && (
        <label className="block text-sm font-medium text-gray-300">
          {label}
        </label>
      )}

      {!hideSearchInput && (
        <input
          type="text"
          placeholder={placeholder}
          onChange={(e) => debouncedFilter(e.target.value)}
          className="w-full px-3 py-2 text-sm border border-gray-700 bg-gray-800 rounded-t-md placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
      )}

      <div
        className={`border border-gray-700 overflow-hidden ${
          hideSearchInput ? "rounded-md" : "rounded-b-md border-t-0"
        }`}
        style={{ height }}
      >
        <AutoSizer disableHeight>
          {({ width }) => (
            <List
              height={height}
              width={width}
              itemCount={filteredOptions.length}
              itemSize={itemHeight}
            >
              {Row}
            </List>
          )}
        </AutoSizer>
      </div>

      {selected.length > 0 && (
        <div className="text-xs text-gray-500 mt-1">
          Selected: {selected.join(", ")}
        </div>
      )}
    </div>
  );
}
