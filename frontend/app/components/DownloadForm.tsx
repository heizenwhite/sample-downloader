"use client";

import { useState, useEffect } from "react";
import { v4 as uuidv4 } from "uuid";
import InputField from "./InputField";
import SelectInput from "./SelectInput";
import Spinner from "./Spinner";
import Select from "react-select";

export default function DownloadForm() {
  const [product, setProduct] = useState("Trades");
  const [exchangeCode, setExchangeCode] = useState("");
  const [instrumentClass, setInstrumentClass] = useState<string[]>([]);
  const [instrumentCode, setInstrumentCode] = useState<string[]>([]);
  const [indexCode, setIndexCode] = useState("");
  const [granularity, setGranularity] = useState("1m");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("");
  const [abortController, setAbortController] = useState<AbortController | null>(null);
  const [requestId, setRequestId] = useState<string | null>(null);
  const [bucketType, setBucketType] = useState("indices-backfill");

  const [availableClasses, setAvailableClasses] = useState<string[]>([]);
  const [availableInstrumentCodes, setAvailableInstrumentCodes] = useState<string[]>([]);

  const requiresGranularity = ["OHLCV", "VWAP", "COHLCVVWAP"].includes(product);
  const isIndexProduct = ["Index", "Index Multi-Assets"].includes(product);
  const storage = isIndexProduct ? "wasabi" : "s3";

  useEffect(() => {
    const fetchInstruments = async () => {
      if (!exchangeCode) return;
  
      const exchangeCodes = exchangeCode.split(",").map(e => e.trim()).filter(Boolean);
      if (exchangeCodes.length === 0) return;
  
      try {
        let allClasses = new Set<string>();
        let allSymbols = new Set<string>();
  
        for (const code of exchangeCodes) {
          const url = `https://reference-data-api.kaiko.io/v1/instruments?exchange_code=${code}&page_size=10000`;
          const res = await fetch(url);
          const json = await res.json();
  
          if (json?.data?.length) {
            for (const item of json.data) {
              if (item.kaiko_legacy_symbol) allSymbols.add(item.kaiko_legacy_symbol);
              if (item.class) allClasses.add(item.class);
            }
          }
        }
  
        setAvailableClasses(Array.from(allClasses).sort());
        setAvailableInstrumentCodes(Array.from(allSymbols).sort());
      } catch (err) {
        console.error("Instrument fetch failed:", err);
        setAvailableClasses([]);
        setAvailableInstrumentCodes([]);
      }
    };
  
    // Debounce the fetch (wait 500ms after typing stops)
    const timeout = setTimeout(fetchInstruments, 500);
    return () => clearTimeout(timeout);
  }, [exchangeCode]);
  

  const handleDownload = async () => {
    const id = uuidv4();
    setRequestId(id);
    setLoading(true);
    setStatus("");
    const controller = new AbortController();
    setAbortController(controller);

    try {
      const params: Record<string, string> = {
        product,
        exchange_code: exchangeCode,
        instrument_class: instrumentClass.join(","),
        instrument_code: instrumentCode.join(","),
        index_code: indexCode,
        granularity,
        start_date: startDate,
        end_date: endDate,
        storage,
        request_id: id,
        bucket: bucketType,
      };

      const backendUrl = process.env.NEXT_PUBLIC_API_BASE!;
      const res = await fetch(`${backendUrl}/api/download/download/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(params),
        signal: controller.signal,
      });

      if (!res.ok) {
        const text = await res.text();
        setStatus(`❌ Error: ${text}`);
        return;
      }

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "sample_data.zip";
      a.click();
      setStatus("✅ Download started!");
    } catch (err: any) {
      setStatus(err.name === "AbortError" ? "⚠️ Download cancelled!" : `❌ ${err.message}`);
    } finally {
      setLoading(false);
      setAbortController(null);
      setRequestId(null);
    }
  };

  const cancelDownload = async () => {
    if (abortController) abortController.abort();
    if (requestId) {
      const backendUrl = process.env.NEXT_PUBLIC_API_BASE!;
      await fetch(`${backendUrl}/api/cancel/?request_id=${requestId}`, { method: "POST" });
      setStatus("⚠️ Download cancelled (backend)!");
    }
    setLoading(false);
  };

  return (
    <div className="space-y-4">
      <SelectInput label="Product" value={product} setValue={setProduct} options={[
        "Trades", "Order Book Snapshots", "Full Order Book", "Top Of Book", 
        "OHLCV", "VWAP", "COHLCVVWAP", "Derivatives", "Index", "Index Multi-Assets"
      ]} />

      {!isIndexProduct && (
        <>
          <InputField label="Exchange Code(s)" value={exchangeCode} setValue={setExchangeCode} />

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Instrument Class(es)</label>
            <Select
              isMulti
              options={availableClasses.map((c) => ({ label: c, value: c }))}
              value={instrumentClass.map((v) => ({ label: v, value: v }))}
              onChange={(selected) => setInstrumentClass(selected.map((s) => s.value))}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Instrument Code(s)</label>
            <Select
              isMulti
              options={availableInstrumentCodes.map((c) => ({ label: c, value: c }))}
              value={instrumentCode.map((v) => ({ label: v, value: v }))}
              onChange={(selected) => setInstrumentCode(selected.map((s) => s.value))}
            />
          </div>
        </>
      )}

      {isIndexProduct && (
        <>
          <InputField label="Index Code(s)" value={indexCode} setValue={setIndexCode} />
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">Select Bucket</label>
            <div className="flex items-center space-x-4">
              {["indices-backfill", "indices-data"].map((type) => (
                <label key={type} className="flex items-center space-x-2">
                  <input
                    type="radio"
                    name="bucket"
                    value={type}
                    checked={bucketType === type}
                    onChange={() => setBucketType(type)}
                    className="h-4 w-4"
                  />
                  <span className="text-sm text-gray-600 capitalize">{type.replace("-", " ")}</span>
                </label>
              ))}
            </div>
          </div>
        </>
      )}

      {requiresGranularity && (
        <SelectInput label="Granularity" value={granularity} setValue={setGranularity} options={[
          "1m", "5m", "10m", "15m", "30m", "1h", "4h", "1d"
        ]} />
      )}

      <InputField label="Start Date (YYYY-MM-DD)" value={startDate} setValue={setStartDate} />
      <InputField label="End Date (YYYY-MM-DD)" value={endDate} setValue={setEndDate} />

      <button
        onClick={handleDownload}
        className={`w-full flex justify-center items-center gap-2 ${
          loading ? "bg-gray-400 cursor-not-allowed" : "bg-blue-600 hover:bg-blue-700"
        } text-white py-2 rounded`}
        disabled={loading}
      >
        {loading && <Spinner />}
        {loading ? "Processing..." : "Download CSVs"}
      </button>

      {loading && (
        <button
          onClick={cancelDownload}
          className="w-full bg-red-500 hover:bg-red-600 text-white py-2 rounded"
        >
          Cancel Download
        </button>
      )}

      <div className="mt-4 text-sm bg-gray-100 p-3 rounded min-h-[50px]">{status}</div>
    </div>
  );
}
