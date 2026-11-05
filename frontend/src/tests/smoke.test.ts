import { describe, it, expect } from "vitest";

describe("SentinelX frontend smoke tests", () => {
  it("validates a severity label mapping", () => {
    const severityColor = (sev: string) => {
      switch (sev) {
        case "critical": return "badge-critical";
        case "high": return "badge-high";
        case "medium": return "badge-medium";
        case "low": return "badge-low";
        default: return "badge-unknown";
      }
    };
    expect(severityColor("critical")).toBe("badge-critical");
    expect(severityColor("unknown")).toBe("badge-unknown");
  });

  it("validates an incident status transition order", () => {
    const order = [
      "detection",
      "triage",
      "investigation",
      "containment",
      "recovery",
      "closure",
    ];
    expect(order[0]).toBe("detection");
    expect(order[order.length - 1]).toBe("closure");
  });
});
