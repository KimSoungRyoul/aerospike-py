import { useMemo } from "react";
import type { RecordResponse } from "@/api/types";
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  flexRender,
  type ColumnDef,
  type SortingState,
} from "@tanstack/react-table";
import { useState } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Button } from "@/components/ui/button";
import { ArrowUpDown, MoreHorizontal, Eye, Trash2 } from "lucide-react";
import { EmptyState } from "@/components/common/EmptyState";
import { Database } from "lucide-react";

interface Props {
  records: RecordResponse[];
  onView: (record: RecordResponse) => void;
  onDelete: (record: RecordResponse) => void;
}

function formatBinValue(value: unknown, type: string): string {
  if (value === null || value === undefined) return "null";
  if (type === "map" || type === "list") return JSON.stringify(value);
  if (type === "bytes") return `0x${String(value).slice(0, 16)}...`;
  return String(value);
}

function recordKey(rec: RecordResponse, index: number): string {
  if (rec.key) return `${rec.key[0]}-${rec.key[1]}-${rec.key[2]}`;
  return `row-${index}`;
}

export function RecordTable({ records, onView, onDelete }: Props) {
  const [sorting, setSorting] = useState<SortingState>([]);

  // Collect all bin names
  const binNames = useMemo(() => {
    const names = new Set<string>();
    for (const rec of records) {
      if (rec.bins) {
        for (const name of Object.keys(rec.bins)) {
          names.add(name);
        }
      }
    }
    return Array.from(names).sort();
  }, [records]);

  const columns = useMemo<ColumnDef<RecordResponse>[]>(
    () => [
      {
        id: "pk",
        header: ({ column }) => (
          <Button
            variant="ghost"
            size="sm"
            className="-ml-3 h-8"
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          >
            PK
            <ArrowUpDown className="ml-1 h-3 w-3" />
          </Button>
        ),
        accessorFn: (row) => (row.key ? String(row.key[2]) : "-"),
        cell: ({ getValue }) => (
          <span className="font-mono text-xs">{getValue() as string}</span>
        ),
      },
      {
        id: "gen",
        header: "Gen",
        accessorFn: (row) => row.meta?.gen ?? "-",
        cell: ({ getValue }) => (
          <span className="text-xs">{String(getValue())}</span>
        ),
      },
      {
        id: "ttl",
        header: "TTL",
        accessorFn: (row) => row.meta?.ttl ?? "-",
        cell: ({ getValue }) => (
          <span className="text-xs">{String(getValue())}</span>
        ),
      },
      ...binNames.map<ColumnDef<RecordResponse>>((binName) => ({
        id: `bin_${binName}`,
        header: binName,
        accessorFn: (row) => {
          const bin = row.bins?.[binName];
          return bin ? formatBinValue(bin.value, bin.type) : "-";
        },
        cell: ({ getValue }) => {
          const val = getValue() as string;
          const isLong = val.length > 50;
          const display = isLong ? val.slice(0, 50) + "..." : val;
          if (isLong) {
            return (
              <Tooltip>
                <TooltipTrigger asChild>
                  <span className="max-w-xs truncate font-mono text-xs cursor-default">
                    {display}
                  </span>
                </TooltipTrigger>
                <TooltipContent className="max-w-sm">
                  <p className="break-all font-mono text-xs">{val}</p>
                </TooltipContent>
              </Tooltip>
            );
          }
          return <span className="font-mono text-xs">{val}</span>;
        },
      })),
      {
        id: "actions",
        header: () => <span className="sr-only">Actions</span>,
        cell: ({ row }) => (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="h-7 w-7">
                <MoreHorizontal className="h-3.5 w-3.5" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => onView(row.original)}>
                <Eye className="mr-2 h-4 w-4" />
                View Detail
              </DropdownMenuItem>
              <DropdownMenuItem
                className="text-destructive focus:text-destructive"
                onClick={() => onDelete(row.original)}
              >
                <Trash2 className="mr-2 h-4 w-4" />
                Delete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        ),
      },
    ],
    [binNames, onView, onDelete]
  );

  const table = useReactTable({
    data: records,
    columns,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getRowId: (row, index) => recordKey(row, index),
  });

  if (records.length === 0) {
    return (
      <EmptyState
        icon={Database}
        title="No Records"
        description="No records found in this set."
      />
    );
  }

  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          {table.getHeaderGroups().map((headerGroup) => (
            <TableRow key={headerGroup.id}>
              {headerGroup.headers.map((header) => (
                <TableHead key={header.id}>
                  {header.isPlaceholder
                    ? null
                    : flexRender(header.column.columnDef.header, header.getContext())}
                </TableHead>
              ))}
            </TableRow>
          ))}
        </TableHeader>
        <TableBody>
          {table.getRowModel().rows.map((row) => (
            <TableRow key={row.id} className="hover:bg-muted/50">
              {row.getVisibleCells().map((cell) => (
                <TableCell key={cell.id}>
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
