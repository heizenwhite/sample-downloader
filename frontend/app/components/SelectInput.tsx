"use client";

import React from "react";

type Props = {
  label: string;
  value: string | string[];
  setValue: (val: string | string[]) => void;
  options: string[];
  multi?: boolean;
};

export default function SelectInput({ label, value, setValue, options, multi = false }: Props) {
  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    if (multi) {
      const selected = Array.from(e.target.selectedOptions, (opt) => opt.value);
      setValue(selected);
    } else {
      setValue(e.target.value);
    }
  };

  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
      <select
        multiple={multi}
        value={value}
        onChange={handleChange}
        className="w-full border border-gray-300 rounded px-3 py-2"
      >
        {!multi && <option value="">Select</option>}
        {options.map((opt) => (
          <option key={opt} value={opt}>
            {opt}
          </option>
        ))}
      </select>
    </div>
  );
}
