type Props = {
    label: string;
    value: string;
    setValue: (val: string) => void;
    options: string[];
  };
  
  export default function SelectInput({ label, value, setValue, options }: Props) {
    return (
      <div>
        <label className="block mb-1 font-medium">{label}</label>
        <select
          value={value}
          onChange={(e) => setValue(e.target.value)}
          className="w-full border p-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-400"
        >
          {options.map((opt) => (
            <option key={opt} value={opt}>
              {opt}
            </option>
          ))}
        </select>
      </div>
    );
  }
  