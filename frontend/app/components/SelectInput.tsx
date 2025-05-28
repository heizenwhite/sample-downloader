// app/components/SelectInput.tsx
"use client";

import React from "react";

type Props = {
  value: string | string[];
  setValue: (val: string | string[]) => void;
  options: string[];
  multi?: boolean;
  /** wrapper div classes (spacing, background, etc.) */
  className?: string;
  /** classes applied directly to the <select> element */
  selectClassName?: string;
};

export default function SelectInput({
  value,
  setValue,
  options,
  multi = false,
  className = "",
  selectClassName = "",
}: Props) {
  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    if (multi) {
      const selected = Array.from(e.target.selectedOptions, (opt) => opt.value);
      setValue(selected);
    } else {
      setValue(e.target.value);
    }
  };

  return (
    <div className={className}>
      <select
        multiple={multi}
        value={value}
        onChange={handleChange}
        className={`
          w-full border border-gray-300 rounded px-3 py-2
          focus:outline-none focus:ring-2 focus:ring-blue-500
          ${selectClassName}
        `}
      >
        {!multi && <option value="">Select...</option>}
        {options.map((opt) => (
          <option key={opt} value={opt}>
            {opt}
          </option>
        ))}
      </select>
    </div>
  );
}
