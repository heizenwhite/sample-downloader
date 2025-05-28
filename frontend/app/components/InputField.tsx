// app/components/InputField.tsx
import React from "react";

type Props = {
  value: string;
  setValue: (val: string) => void;
  className?: string;       // wrapper class
  inputClassName?: string;  // class for the <input>
};

export default function InputField({
  value,
  setValue,
  className = "",
  inputClassName = "",
}: Props) {
  return (
    <div className={className}>
      <input
        type="text"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        className={`
          w-full border border-gray-700 bg-gray-800 text-white
          p-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-500
          ${inputClassName}
        `}
      />
    </div>
  );
}
