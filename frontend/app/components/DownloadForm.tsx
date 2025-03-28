"use client";

import { useState } from "react";
import { v4 as uuidv4 } from "uuid";
import InputField from "./InputField";
import SelectInput from "./SelectInput";
import Spinner from "./Spinner";

export default function DownloadForm() {
  const [product, setProduct] = useState("Trades");
  const [exchangeCode, setExchangeCode] = useState("");
  const [instrumentClass, setInstrumentClass] = useState("");
  const [instrumentCode, setInstrumentCode] = useState("");
  const [indexCode, setIndexCode] = useState("");
  const [granularity, setGranularity] = useState("1m");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("");
  const [abortController, setAbortController] = useState<AbortController | null>(null);
  const [requestId, setRequestId] = useState<string | null>(null);

  const [bucketType, setBucketType] = useState("indices-backfill");

  const requiresGranularity = ["OHLCV", "VWAP", "COHLCVVWAP"].includes(product);
  const isIndexProduct = ["Index", "Index Multi-Assets"].includes(product);
  const storage = isIndexProduct ? "wasabi" : "s3";

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
        instrument_class: instrumentClass,
        instrument_code: instrumentCode,
        index_code: indexCode,
        granularity,
        start_date: startDate,
        end_date: endDate,
        storage,
        request_id: id,
        bucket: bucketType,
      };

      const urlParams = new URLSearchParams();
      Object.entries(params).forEach(([key, val]) => {
        if (val) urlParams.append(key, val);
      });

      const backendUrl = process.env.NEXT_PUBLIC_API_BASE!;

      const res = await fetch(`${backendUrl}/api/download/download/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
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
      if (err.name === "AbortError") {
        setStatus("⚠️ Download cancelled!");
      } else {
        setStatus(`❌ ${err.message}`);
      }
    } finally {
      setLoading(false);
      setAbortController(null);
      setRequestId(null);
    }
  };

  const cancelDownload = async () => {
    if (abortController) {
      abortController.abort();
    }
  
    if (requestId) {
      const backendUrl = process.env.NEXT_PUBLIC_API_BASE!;
      await fetch(`${backendUrl}/api/cancel/?request_id=${requestId}`, {
        method: "POST",
      });
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
          <InputField label="Instrument Class(es)" value={instrumentClass} setValue={setInstrumentClass} />
          <InputField label="Instrument Code(s)" value={instrumentCode} setValue={setInstrumentCode} />
        </>
      )}

      {isIndexProduct && (
        <>
          <InputField label="Index Code(s)" value={indexCode} setValue={setIndexCode} />

          {/* Radio buttons for bucket selection */}
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">Select Bucket</label>
            <div className="flex items-center space-x-4">
              <div className="flex items-center">
                <input
                  type="radio"
                  id="indices-backfill"
                  name="bucket"
                  value="indices-backfill"
                  checked={bucketType === "indices-backfill"}
                  onChange={() => setBucketType("indices-backfill")}
                  className="h-4 w-4 text-indigo-600 border-gray-300 focus:ring-indigo-500"
                />
                <label htmlFor="indices-backfill" className="ml-2 text-sm text-gray-600">Indices Backfill</label>
              </div>
              <div className="flex items-center">
                <input
                  type="radio"
                  id="indices-data"
                  name="bucket"
                  value="indices-data"
                  checked={bucketType === "indices-data"}
                  onChange={() => setBucketType("indices-data")}
                  className="h-4 w-4 text-indigo-600 border-gray-300 focus:ring-indigo-500"
                />
                <label htmlFor="indices-data" className="ml-2 text-sm text-gray-600">Indices Data</label>
              </div>
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
