type Props = {
    label: string;
    value: string;
    setValue: (val: string) => void;
  };
  
  export default function InputField({ label, value, setValue }: Props) {
    return (
      <div>
        <label className="block mb-1 font-medium">{label}</label>
        <input
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          className="w-full border p-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-400"
        />
      </div>
    );
  }
  