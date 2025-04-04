"use client";

import { useEffect, useState, useCallback } from "react";
import { v4 as uuidv4 } from "uuid";
import InputField from "./InputField";
import SelectInput from "./SelectInput";
import Spinner from "./Spinner";
import dynamic from "next/dynamic";
import debounce from "lodash.debounce";

// Lazy load the virtualized multiselect component
const MultiSelect = dynamic(() => import("./VirtualizedMultiSelect"), { ssr: false });

const KAIKO_INSTRUMENTS_API = "https://reference-data-api.kaiko.io/v1/instruments";

export default function DownloadForm() {
  const [product, setProduct] = useState("Trades");
  const [exchangeCode, setExchangeCode] = useState("");
  const [instrumentClass, setInstrumentClass] = useState<string[]>([]);
  const [instrumentCode, setInstrumentCode] = useState<string[]>([]);
  const [rawInstruments, setRawInstruments] = useState<any[]>([]);
  const [indexCode, setIndexCode] = useState("");
  const [granularity, setGranularity] = useState("1m");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<{
    inputs?: Record<string, string>;
    prefixes?: string[];
    log?: string[];
    error?: string;
  } | null>(null);
  const [abortController, setAbortController] = useState<AbortController | null>(null);
  const [requestId, setRequestId] = useState<string | null>(null);
  const [bucketType, setBucketType] = useState("indices-backfill");

  const [availableClasses, setAvailableClasses] = useState<string[]>([]);
  const [availableCodes, setAvailableCodes] = useState<string[]>([]);

  const requiresGranularity = ["OHLCV", "VWAP", "COHLCVVWAP"].includes(product);
  const isIndexProduct = ["Index", "Index Multi-Assets"].includes(product);
  const storage = isIndexProduct ? "wasabi" : "s3";

  const debouncedFetchInstruments = debounce(async (
    exchange: string,
    isIndexProduct: boolean,
    setRawInstruments: Function,
    setAvailableClasses: Function
  ) => {
    if (!exchange || isIndexProduct) return;

    const exchanges = exchange.split(",").map((e) => e.trim());
    const allInstruments: any[] = [];
    const uniqueClasses = new Set<string>();

    try {
      for (const ex of exchanges) {
        let token: string | null = null;

        do {
          const params = new URLSearchParams({
            exchange_code: ex,
            ...(token ? { continuation_token: token } : {}),
            page_size: "500",
          });

          const res = await fetch(`${KAIKO_INSTRUMENTS_API}?${params}`);
          const data = await res.json();

          if (Array.isArray(data.data)) {
            for (const item of data.data) {
              allInstruments.push(item);
              if (item.class) uniqueClasses.add(item.class);
            }
          }

          token = data.continuation_token || null;
        } while (token);
      }

      setRawInstruments(allInstruments);
      setAvailableClasses(Array.from(uniqueClasses).sort());
    } catch (err) {
      console.error("Instrument fetch failed:", err);
    }
  }, 500);

  useEffect(() => {
    if (!isIndexProduct && exchangeCode) {
      debouncedFetchInstruments(exchangeCode, isIndexProduct, setRawInstruments, setAvailableClasses);
    } else {
      setRawInstruments([]);
      setAvailableClasses([]);
      setAvailableCodes([]);
    }
  }, [exchangeCode, isIndexProduct]);

  useEffect(() => {
    if (!isIndexProduct && rawInstruments.length > 0) {
      const filtered = rawInstruments.filter((item) =>
        instrumentClass.length === 0 || instrumentClass.includes(item.class)
      );

      const symbols = Array.from(
        new Set(filtered.map((item) => item.kaiko_legacy_symbol).filter(Boolean))
      ).sort();

      setAvailableCodes(symbols);
    }
  }, [instrumentClass, rawInstruments, isIndexProduct]);

  const handleDownload = async () => {
    const id = uuidv4();
    setRequestId(id);
    setLoading(true);
    setStatus(null);
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

      const isJson = res.headers.get("Content-Type")?.includes("application/json");
      if (isJson) {
        const result = await res.json();
        setStatus(result);
      } else {
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `${product.replace(/\s+/g, "_")}.zip`;
        a.click();
        setStatus({ log: ["✅ Download started!"], inputs: params });
      }
    } catch (err: any) {
      if (err.name === "AbortError") {
        setStatus({ log: ["⚠️ Download cancelled!"] });
      } else {
        setStatus({ error: `❌ ${err.message}` });
      }
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
      setStatus({ log: ["⚠️ Download cancelled (backend)!"] });
    }
    setLoading(false);
  };

  return (
    <div className="space-y-4">
      <SelectInput
        label="Product"
        value={product}
        setValue={setProduct}
        options={[
          "Trades", "Order Book Snapshots", "Full Order Book", "Top Of Book",
          "OHLCV", "VWAP", "COHLCVVWAP", "Derivatives", "Index", "Index Multi-Assets"
        ]}
      />

      {!isIndexProduct && (
        <>
          <InputField label="Exchange Code(s)" value={exchangeCode} setValue={setExchangeCode} />

          <MultiSelect
            label="Instrument Class(es)"
            options={availableClasses}
            selected={instrumentClass}
            onChange={setInstrumentClass}
            placeholder="Select class(es)..."
          />

          <MultiSelect
            label="Instrument Code(s)"
            options={availableCodes}
            selected={instrumentCode}
            onChange={setInstrumentCode}
            placeholder="Select code(s)..."
          />
        </>
      )}

      {isIndexProduct && (
        <>
          <InputField label="Index Code(s)" value={indexCode} setValue={setIndexCode} />
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">Select Bucket</label>
            <div className="flex space-x-4">
              {["indices-backfill", "indices-data"].map(bucket => (
                <label key={bucket} className="flex items-center space-x-2">
                  <input
                    type="radio"
                    name="bucket"
                    value={bucket}
                    checked={bucketType === bucket}
                    onChange={() => setBucketType(bucket)}
                    className="h-4 w-4 text-indigo-600"
                  />
                  <span className="text-sm text-gray-600 capitalize">{bucket.replace("-", " ")}</span>
                </label>
              ))}
            </div>
          </div>
        </>
      )}

      {requiresGranularity && (
        <SelectInput
          label="Granularity"
          value={granularity}
          setValue={setGranularity}
          options={["1m", "5m", "10m", "15m", "30m", "1h", "4h", "1d"]}
        />
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

      <div className="mt-4 text-sm bg-gray-100 p-3 rounded whitespace-pre-wrap">
        {status && (
          <>
            {status.inputs && (
              <div>
                <strong>📥 Inputs:</strong> {JSON.stringify(status.inputs, null, 2)}
              </div>
            )}
            {status.prefixes && (
              <div className="mt-2">
                <strong>📁 Generated Prefixes:</strong>
                <ul className="list-disc pl-5">
                  {status.prefixes.map((prefix, idx) => (
                    <li key={idx}>{prefix}</li>
                  ))}
                </ul>
              </div>
            )}
            {status.log && (
              <div className="mt-2">
                {status.log.map((line, idx) => (
                  <div key={idx}>{line}</div>
                ))}
              </div>
            )}
            {status.error && (
              <div className="text-red-600 mt-2">{status.error}</div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
