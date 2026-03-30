// SPDX-License-Identifier: AGPL-3.0-only
// Copyright 2026-present the Unsloth AI Inc. team. All rights reserved. See /studio/LICENSE.AGPL-3.0

import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { authFetch } from "@/features/auth/api";
import { motion } from "motion/react";

interface SplashScreenProps {
  onStartOnboarding: () => void;
  onGoToStudio: () => void;
}

interface ChinaMirrorState {
  enabled: boolean;
  hf_endpoint: string | null;
}

export function SplashScreen({
  onStartOnboarding,
  onGoToStudio,
}: SplashScreenProps) {
  const [mirrorEnabled, setMirrorEnabled] = useState(false);
  const [mirrorLoading, setMirrorLoading] = useState(false);

  // Fetch current mirror state on mount
  useEffect(() => {
    let cancelled = false;
    authFetch("/api/settings/china-mirror")
      .then((res) => {
        if (res.ok && !cancelled) return res.json();
        return null;
      })
      .then((data: ChinaMirrorState | null) => {
        if (data && !cancelled) setMirrorEnabled(data.enabled);
      })
      .catch(() => {
        // Non-critical: if the fetch fails just keep default (off)
      });
    return () => {
      cancelled = true;
    };
  }, []);

  async function handleMirrorToggle(checked: boolean) {
    setMirrorLoading(true);
    try {
      const res = await authFetch("/api/settings/china-mirror", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ enabled: checked }),
      });
      if (res.ok) {
        setMirrorEnabled(checked);
      }
    } catch {
      // Silently ignore — the user can retry
    } finally {
      setMirrorLoading(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-gradient-to-b from-background via-background to-primary/5 p-6">
      <Card className="w-full max-w-md px-8 py-8 shadow-border ring-1 ring-border">
        {/* Mascot */}
        <div className="flex justify-center">
          <motion.img
            src="/Sloth emojis/Sloth loca pc.png"
            alt="Sloth mascot"
            className="size-30"
            initial={{ opacity: 0, y: 40, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{
              type: "spring",
              duration: 0.7,
              bounce: 0.3,
              delay: 0.1,
            }}
          />
        </div>

        {/* Brand text */}
        <motion.div
          className="mt-4 flex flex-col items-center gap-1"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{
            duration: 0.4,
            ease: [0.165, 0.84, 0.44, 1],
            delay: 0.4,
          }}
        >
          <h1 className="text-2xl font-semibold tracking-tight">
            Unsloth Studio
          </h1>
          <p className="text-sm text-muted-foreground">Train and run LLMs locally</p>
        </motion.div>

        {/* Buttons */}
        <motion.div
          className="mt-8 flex flex-col gap-3"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{
            duration: 0.4,
            ease: [0.165, 0.84, 0.44, 1],
            delay: 0.8,
          }}
        >
          <Button size="lg" onClick={onStartOnboarding}>
            Start Onboarding
          </Button>
          <Button size="lg" variant="outline" onClick={onGoToStudio}>
            Skip Onboarding
          </Button>
        </motion.div>

        {/* China mainland mirror toggle */}
        <motion.div
          className="mt-5 flex items-center justify-between gap-3 rounded-lg border border-border bg-muted/40 px-4 py-3"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{
            duration: 0.4,
            ease: [0.165, 0.84, 0.44, 1],
            delay: 1.1,
          }}
        >
          <div className="flex flex-col gap-0.5">
            <span className="text-sm font-medium leading-none">
              China Mainland Optimization
            </span>
            <span className="text-xs text-muted-foreground">
              Use domestic mirrors for faster downloads
            </span>
          </div>
          <Switch
            size="sm"
            checked={mirrorEnabled}
            onCheckedChange={handleMirrorToggle}
            disabled={mirrorLoading}
          />
        </motion.div>
      </Card>
    </div>
  );
}
