"use client";

import { useState } from "react";
import { v4 as uuidv4 } from 'uuid';
import InputField from "./InputField";
import SelectInput from "./SelectInput";
import Spinner from "./Spinner";

export default function DownloadForm() {
  const [product, setProduct] = useState("Trades");
  const [exchangeCode, setExchangeCode] = useState("");
  const [instrumentClass, setInstrumentClass] = useState("");
  const [instrumentCode, setInstrumentCode] = useState("");
  const [indexCode, setIndexCode] = useState("");
  const [granularity, setGranularity] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [mfaArn, setMfaArn] = useState("");
  const [mfaCode, setMfaCode] = useState("");
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("");
  const [abortController, setAbortController] = useState<AbortController | null>(null);

  const requiresGranularity = ["OHLCV", "VWAP", "COHLCVVWAP"].includes(product);
  const isIndexProduct = ["Index", "Index Multi-Asset"].includes(product);
  const storage = isIndexProduct ? "wasabi" : "s3";
  const [requestId, setRequestId] = useState<string | null>(null);

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
        mfa_arn: mfaArn,
        mfa_code: mfaCode,
        request_id: id,
      };

      const urlParams = new URLSearchParams();
      Object.entries(params).forEach(([key, val]) => {
        if (val) urlParams.append(key, val);
      });

      const backendUrl = "http://localhost:8000";

      const res = await fetch(`${backendUrl}/api/download/download/?${urlParams.toString()}`, {
        method: "POST",
        signal: controller.signal,
      });

      if (!res.ok) {
        const text = await res.text();
        setStatus(`❌ Error: ${text}`);
        setLoading(false);
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
      await fetch(`http://localhost:8000/api/cancel/?request_id=${requestId}`, { method: "POST" });
      setStatus("⚠️ Download cancelled (backend)!");
    }
    setLoading(false);
  };

  return (
    <div className="space-y-4">
      <SelectInput label="Product" value={product} setValue={setProduct} options={[
        "Trades", "Order Book Snapshots", "Full Order Book", "Top Of Book", 
        "OHLCV", "VWAP", "COHLCVVWAP", "Derivatives", "Index", "Index Multi-Asset"
      ]} />

      {!isIndexProduct && (
        <>
          <InputField label="Exchange Code(s)" value={exchangeCode} setValue={setExchangeCode} />
          <InputField label="Instrument Class(es)" value={instrumentClass} setValue={setInstrumentClass} />
          <InputField label="Instrument Code(s)" value={instrumentCode} setValue={setInstrumentCode} />
        </>
      )}

      {isIndexProduct && (
        <InputField label="Index Code(s)" value={indexCode} setValue={setIndexCode} />
      )}

      {requiresGranularity && (
        <SelectInput label="Granularity" value={granularity} setValue={setGranularity} options={[
          "1m", "5m", "10m", "15m", "30m", "1h", "4h", "1d"  
        ]} />
      )}

      <InputField label="Start Date (YYYY-MM-DD)" value={startDate} setValue={setStartDate} />
      <InputField label="End Date (YYYY-MM-DD)" value={endDate} setValue={setEndDate} />

      {storage === "s3" && (
        <>
          <InputField label="MFA ARN" value={mfaArn} setValue={setMfaArn} />
          <InputField label="MFA Code" value={mfaCode} setValue={setMfaCode} />
        </>
      )}

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
