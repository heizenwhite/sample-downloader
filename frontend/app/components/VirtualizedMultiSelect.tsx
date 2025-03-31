"use client";

import React, { useState, useMemo } from "react";
import { FixedSizeList as List } from "react-window";
import AutoSizer from "react-virtualized-auto-sizer";
import { debounce } from "lodash";

type Option = string;

type Props = {
  label?: string;
  options: Option[];
  selected: Option[];
  onChange: (selected: Option[]) => void;
  placeholder?: string;
  height?: number;
  itemHeight?: number;
};

export default function VirtualizedMultiSelect({
  label,
  options,
  selected = [],
  onChange,
  placeholder = "Select options...",
  height = 200,
  itemHeight = 36,
}: Props) {
  const [filter, setFilter] = useState("");

  const filteredOptions = useMemo(() => {
    return options.filter((opt) =>
      opt.toLowerCase().includes(filter.toLowerCase())
    );
  }, [options, filter]);

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

  const Row = ({ index, style }: { index: number; style: React.CSSProperties }) => {
    const value = filteredOptions[index];
    const isChecked = Array.isArray(selected) && selected.includes(value);
    return (
      <div
        style={style}
        className="px-2 py-1 cursor-pointer hover:bg-blue-100 flex items-center"
        onClick={() => toggleOption(value)}
      >
        <input
          type="checkbox"
          className="mr-2"
          checked={isChecked}
          onChange={() => {}}
          onClick={(e) => e.stopPropagation()}
        />
        <span className="truncate">{value}</span>
      </div>
    );
  };

  return (
    <div className="space-y-1">
      {label && <label className="block text-sm font-medium text-gray-700">{label}</label>}
      <input
        type="text"
        placeholder={placeholder}
        onChange={(e) => debouncedFilter(e.target.value)}
        className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
      />
      <div
        className="border border-gray-300 rounded-md overflow-hidden"
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
      {Array.isArray(selected) && selected.length > 0 && (
        <div className="text-xs text-gray-600 mt-1">
            Selected: {selected.join(", ")}
        </div>
      )}

    </div>
  );
}
