// app/components/DownloadForm.tsx
"use client";

import { useEffect, useState } from "react";
import { v4 as uuidv4 } from "uuid";
import dynamic from "next/dynamic";
import debounce from "lodash.debounce";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import { auth } from "../utils/firebase";
import InputField from "./InputField";
import SelectInput from "./SelectInput";
import Spinner from "./Spinner";

const VirtualizedMultiSelect = dynamic(
  () => import("./VirtualizedMultiSelect"),
  { ssr: false }
);

const KAIKO_INSTRUMENTS_API = "https://reference-data-api.kaiko.io/v1/instruments";

export default function DownloadForm() {
  const [product, setProduct] = useState("Trades");
  const [exchangeCode, setExchangeCode] = useState("");
  const [instrumentClass, setInstrumentClass] = useState<string[]>([]);
  const [instrumentCode, setInstrumentCode] = useState<string[]>([]);
  const [rawInstruments, setRawInstruments] = useState<any[]>([]);
  const [indexCode, setIndexCode] = useState("");
  const [granularity, setGranularity] = useState("1m");
  const [startDate, setStartDate] = useState<Date | null>(null);
  const [endDate, setEndDate] = useState<Date | null>(null);
  const [codeFilter, setCodeFilter] = useState("");
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<{
    inputs?: Record<string, string>;
    log?: string[];
    error?: string;
    downloaded_files?: string[];
    skipped_files?: { key: string; reason: string }[];
  } | null>(null);
  const [abortController, setAbortController] = useState<AbortController | null>(null);
  const [requestId, setRequestId] = useState<string | null>(null);
  const [bucketType, setBucketType] = useState("indices-backfill");

  const [availableClasses, setAvailableClasses] = useState<string[]>([]);
  const [availableCodes, setAvailableCodes] = useState<string[]>([]);

  const requiresGranularity = ["OHLCV", "VWAP", "COHLCVVWAP"].includes(product);
  const isIndexProduct = ["Index", "Index Multi-Assets"].includes(product);
  const storage = isIndexProduct ? "wasabi" : "s3";

  // fetch instrument classes once user enters an exchange
  const debouncedFetch = debounce(
    async (exchange: string) => {
      if (!exchange || isIndexProduct) return;
      const exchanges = exchange.split(",").map((e) => e.trim());
      const all: any[] = [];
      const classes = new Set<string>();

      try {
        for (const ex of exchanges) {
          let token: string | null = null;
          do {
            const params = new URLSearchParams({
              exchange_code: ex,
              ...(token ? { continuation_token: token } : {}),
              page_size: "500",
            });
            const res: Response = await fetch(`${KAIKO_INSTRUMENTS_API}?${params}`);
            const json: { data?: any[]; continuation_token?: string } = await res.json();
            json.data?.forEach((i: any) => {
              all.push(i);
              i.class && classes.add(i.class);
            });
            token = json.continuation_token || null;
          } while (token);
        }
        setRawInstruments(all);
        setAvailableClasses(Array.from(classes).sort());
      } catch {
        /* swallow */
      }
    },
    500,
    { leading: false }
  );

  const displayedCodes = availableCodes.filter((c) =>
    c.toLowerCase().includes(codeFilter.toLowerCase())
  );

  useEffect(() => {
    if (!isIndexProduct && exchangeCode) {
      debouncedFetch(exchangeCode);
    } else {
      setRawInstruments([]);
      setAvailableClasses([]);
      setAvailableCodes([]);
    }
  }, [exchangeCode, isIndexProduct]);

  useEffect(() => {
    if (!isIndexProduct && rawInstruments.length) {
      const filtered = rawInstruments.filter((i) =>
        !instrumentClass.length || instrumentClass.includes(i.class)
      );
      const syms = Array.from(
        new Set(filtered.map((i) => i.kaiko_legacy_symbol).filter(Boolean))
      ).sort();
      setAvailableCodes(syms);
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
      const payload = {
        product,
        exchange_code: exchangeCode,
        instrument_class: instrumentClass.join(","),
        instrument_code: instrumentCode.join(","),
        index_code: indexCode,
        granularity,
        start_date: startDate?.toISOString() ?? "",
        end_date: endDate?.toISOString() ?? "",
        storage,
        request_id: id,
        bucket: bucketType,
      };
      const user = auth!.currentUser;
      if (!user) throw new Error("You must be signed in");
      const token = await user.getIdToken();
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE}/api/download/download/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(payload),
          signal: controller.signal,
        }
      );
      const isJson = res.headers
        .get("Content-Type")
        ?.includes("application/json");
      if (isJson) {
        setStatus(await res.json());
      } else {
        // parse headers & download
        const dl = (res.headers.get("X-Downloaded-Files") || "")
          .split(",")
          .filter(Boolean);
        const sk = (res.headers.get("X-Skipped-Files") || "")
          .split(",")
          .map((e) => {
            const [key, reason] = e.split("::");
            return { key, reason };
          });
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `${product.replace(/\s+/g, "_")}.zip`;
        a.click();
        setStatus({ downloaded_files: dl, skipped_files: sk });
      }
    } catch (err: any) {
      if (err.name === "AbortError") {
        setStatus({ log: ["⚠️ Download cancelled"] });
      } else {
        setStatus({ error: err.message });
      }
    } finally {
      setLoading(false);
      setAbortController(null);
      setRequestId(null);
    }
  };

  const cancelDownload = async () => {
    abortController?.abort();
    if (requestId) {
      await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE}/api/cancel/?request_id=${requestId}`,
        { method: "POST" }
      );
      setStatus({ log: ["⚠️ Download cancelled (backend)"] });
    }
    setLoading(false);
  };

  return (
    <div className="bg-gray-900/60 backdrop-blur-md rounded-lg p-8 shadow-xl space-y-6">
      {/* --- Product --- */}
      <div className="space-y-1">
        <label className="block text-sm font-medium text-gray-300">Product</label>
        <SelectInput
          value={product}
          setValue={(v) => setProduct(v as string)}
          options={[
            "Trades",
            "Order Book Snapshots",
            "Full Order Book",
            "Top Of Book",
            "OHLCV",
            "VWAP",
            "COHLCVVWAP",
            "Derivatives",
            "Index",
            "Index Multi-Assets",
          ]}
          className="bg-gray-800 rounded-lg"
          selectClassName="w-full bg-gray-800 text-white text-sm px-4 py-2 rounded-lg"
        />
      </div>

      {/* --- Exchange Code(s) --- */}
      {!isIndexProduct && (
        <div className="space-y-1">
          <label className="block text-sm font-medium text-gray-300">
            Exchange Code(s)
          </label>
          <InputField
            value={exchangeCode}
            setValue={setExchangeCode}
            className="bg-gray-800 rounded-lg"
            inputClassName="w-full bg-gray-800 text-white text-sm px-4 py-2 rounded-lg"
          />
        </div>
      )}

      {/* --- Instrument Class(es) --- */}
      {!isIndexProduct && (
        <div className="space-y-1">
          <label className="block text-sm font-medium text-gray-300">
            Instrument Class(es)
          </label>

          {/* no built-in filter, just the styled list */}
          <VirtualizedMultiSelect
            options={availableClasses}
            selected={instrumentClass}
            onChange={setInstrumentClass}
            placeholder="Pick class(es)…"
            hideSearchInput
            height={150}
            itemHeight={32}
            className="bg-gray-800 rounded-lg border border-gray-700 p-2"
          />
        </div>
      )}


      {/* --- Instrument Code(s) --- */}
      {!isIndexProduct && (
        <div className="space-y-1">
          <label className="block text-sm font-medium text-gray-300">
            Instrument Code(s)
          </label>

          {/* filter + toolbar in one “header” bar */}
          <div className="relative">
            <input
              type="text"
              placeholder="Filter codes…"
              value={codeFilter}
              onChange={(e) => setCodeFilter(e.target.value)}
              className="
                w-full
                bg-gray-800
                text-white
                placeholder-gray-500
                text-sm
                px-4 py-2
                rounded-t-lg
                border border-b-0 border-gray-700
                focus:outline-none focus:ring-2 focus:ring-indigo-500
              "
            />

            <div className="absolute top-2 right-4 flex space-x-3 text-xs">
              <button
                type="button"
                onClick={() => setInstrumentCode(displayedCodes)}
                className="text-indigo-400 hover:text-indigo-300"
              >
                Select All
              </button>
              <button
                type="button"
                onClick={() => setInstrumentCode([])}
                className="text-red-400 hover:text-red-300"
              >
                Clear
              </button>
            </div>
          </div>

          {/* the pick list, styled to match */}
          <VirtualizedMultiSelect
            options={displayedCodes}
            selected={instrumentCode}
            onChange={setInstrumentCode}
            placeholder="Pick one or more codes…"
            hideSearchInput
            height={150}
            itemHeight={32}
            className="
              bg-gray-800
              rounded-b-lg
              border border-gray-700 border-t-0
              p-2
            "
          />
        </div>
      )}



      {/* --- Index Code(s) --- */}
      {isIndexProduct && (
        <div className="space-y-1">
          <label className="block text-sm font-medium text-gray-300">Index Code(s)</label>
          <InputField
            value={indexCode}
            setValue={setIndexCode}
            className="bg-gray-800 rounded-lg"
            inputClassName="w-full bg-gray-800 text-white text-sm px-4 py-2 rounded-lg"
          />
        </div>
      )}

      {/* --- Bucket --- */}
      {isIndexProduct && (
        <div className="space-y-1">
          <label className="block text-sm font-medium text-gray-300">Bucket</label>
          <div className="bg-gray-800 rounded-lg border border-gray-700 px-4 py-3 flex justify-between items-center">
            {["indices-backfill", "indices-data"].map((b) => (
              <label key={b} className="flex items-center space-x-2 text-sm text-white">
                <input
                  type="radio"
                  name="bucket"
                  value={b}
                  checked={bucketType === b}
                  onChange={() => setBucketType(b)}
                  className="h-4 w-4 text-indigo-400 bg-gray-900 border-gray-600 focus:ring-indigo-500"
                />
                <span>{b.replace("-", " ")}</span>
              </label>
            ))}
          </div>
        </div>
      )}

      {/* --- Granularity --- */}
      {requiresGranularity && (
        <div className="space-y-1">
          <label className="block text-sm font-medium text-gray-300">Granularity</label>
          <SelectInput
            value={granularity}
            setValue={(v) => setGranularity(v as string)}
            options={["1m","5m","10m","15m","30m","1h","4h","1d"]}
            className="bg-gray-800 rounded-lg"
            selectClassName="w-full bg-gray-800 text-white text-sm px-4 py-2 rounded-lg"
          />
        </div>
      )}


      {/* Dates */}
      <div className="flex mt-4">
        {/* Start Date (left) */}
        <div className="flex flex-col items-start w-1/2">
          <label className="block text-sm font-medium text-gray-300 mb-1">
            Start Date
          </label>
          <DatePicker
            selected={startDate}
            onChange={setStartDate}
            dateFormat="yyyy-MM-dd"
            placeholderText="Select start"
            className="w-full bg-gray-800 text-white placeholder-gray-500 rounded-md border border-gray-700 px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        {/* End Date (right, pushed a bit) */}
        <div className="flex flex-col items-start w-1/2 ml-8">
          <label className="block text-sm font-medium text-gray-300 mb-1">
            End Date
          </label>
          <DatePicker
            selected={endDate}
            onChange={setEndDate}
            dateFormat="yyyy-MM-dd"
            placeholderText="Select end"
            className="w-full bg-gray-800 text-white placeholder-gray-500 rounded-md border border-gray-700 px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
      </div>

      {/* Download button */}
      <button
        onClick={handleDownload}
        disabled={loading}
        className={`w-full flex justify-center items-center gap-2 text-white font-medium py-3 rounded-md transition
          ${
            loading
              ? "bg-indigo-700 cursor-wait"
              : "bg-indigo-600 hover:bg-indigo-500"
          }`}
      >
        {loading && <Spinner />}
        {loading ? "Processing…" : "Download CSVs"}
      </button>

      {/* Cancel */}
      {loading && (
        <button
          onClick={cancelDownload}
          className="w-full bg-red-600 hover:bg-red-500 text-white py-2 rounded-md"
        >
          Cancel
        </button>
      )}

      {/* Status */}
      {status && (
        <div className="mt-4 text-sm bg-gray-800 text-white p-4 rounded-md space-y-2">
          {status.downloaded_files?.length && (
            <div>
              <strong>✅ Downloaded:</strong>{" "}
              {status.downloaded_files.join(", ")}
            </div>
          )}
          {status.skipped_files?.length && (
            <div>
              <strong>⚠️ Skipped:</strong>{" "}
              {status.skipped_files.map((s) => s.key).join(", ")}
            </div>
          )}
          {status.log?.map((l, i) => (
            <div key={i}>{l}</div>
          ))}
          {status.error && <div className="text-red-400">{status.error}</div>}
        </div>
      )}
    </div>
  );
}
