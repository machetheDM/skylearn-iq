import React, { useEffect, useState } from "react";
import {
  View, Text, ScrollView, TouchableOpacity,
  StyleSheet, ActivityIndicator, RefreshControl,
} from "react-native";
import { useRouter } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { useAuth } from "../../context/AuthContext";
import { API_URL } from "../../constants/api";
import { C } from "../../constants/colors";

type Session = {
  id: number;
  assessment_id: number;
  status: string;
  started_at: string;
  completed_at: string | null;
  score: { percentage: number; pass_fail: boolean | null } | null;
};

export default function HomeScreen() {
  const { user, token } = useAuth();
  const router = useRouter();
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading]   = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  async function fetchSessions() {
    try {
      const res = await fetch(`${API_URL}/api/sessions/learner/my-sessions`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) setSessions(await res.json());
    } catch {}
    finally { setLoading(false); setRefreshing(false); }
  }

  useEffect(() => { fetchSessions(); }, []);

  const completed  = sessions.filter(s => s.status === "COMPLETED");
  const inProgress = sessions.filter(s => s.status === "IN_PROGRESS");
  const avgScore   = completed.length
    ? Math.round(completed.reduce((a, s) => a + (s.score?.percentage ?? 0), 0) / completed.length)
    : 0;
  const passCount  = completed.filter(s => s.score?.pass_fail === true).length;

  return (
    <ScrollView
      style={s.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); fetchSessions(); }} tintColor={C.primary} />}
    >
      {/* Greeting */}
      <View style={s.hero}>
        <Text style={s.greeting}>👋 Hello, {user?.full_name.split(" ")[0]}!</Text>
        <Text style={s.sub}>Ready to learn something today?</Text>
      </View>

      {/* Stats row */}
      <View style={s.statsRow}>
        <StatCard label="Completed" value={completed.length} icon="checkmark-circle-outline" color={C.accent} />
        <StatCard label="Avg Score" value={`${avgScore}%`} icon="trending-up-outline" color={C.primary} />
        <StatCard label="Passed" value={passCount} icon="trophy-outline" color={C.warning} />
      </View>

      {/* In-progress banner */}
      {inProgress.length > 0 && (
        <TouchableOpacity
          style={s.inProgressBanner}
          onPress={() => router.push(`/assessment/session/${inProgress[0].id}`)}
        >
          <Ionicons name="time-outline" size={20} color={C.warning} />
          <Text style={s.inProgressText}>You have an assessment in progress — continue?</Text>
          <Ionicons name="chevron-forward" size={16} color={C.warning} />
        </TouchableOpacity>
      )}

      {/* Quick actions */}
      <Text style={s.sectionTitle}>Quick Actions</Text>
      <View style={s.actionsRow}>
        <ActionCard icon="document-text-outline" label="Take Assessment" onPress={() => router.push("/(tabs)/assessments")} />
        <ActionCard icon="bar-chart-outline" label="View Results" onPress={() => router.push("/(tabs)/results")} />
      </View>

      {/* Recent results */}
      {completed.length > 0 && (
        <>
          <Text style={s.sectionTitle}>Recent Results</Text>
          {completed.slice(0, 3).map(s2 => (
            <TouchableOpacity
              key={s2.id}
              style={s.resultCard}
              onPress={() => router.push(`/assessment/result/${s2.id}`)}
            >
              <View style={{ flex: 1 }}>
                <Text style={s.resultTitle}>Assessment #{s2.assessment_id}</Text>
                <Text style={s.resultDate}>{new Date(s2.completed_at!).toLocaleDateString("en-ZA")}</Text>
              </View>
              <View style={[s.scoreBadge, { backgroundColor: (s2.score?.pass_fail) ? C.accent : C.danger }]}>
                <Text style={s.scoreText}>{Math.round(s2.score?.percentage ?? 0)}%</Text>
              </View>
            </TouchableOpacity>
          ))}
        </>
      )}

      {loading && <ActivityIndicator color={C.primary} style={{ marginTop: 40 }} />}
    </ScrollView>
  );
}

function StatCard({ label, value, icon, color }: { label: string; value: any; icon: any; color: string }) {
  return (
    <View style={[sStat.card, { borderTopColor: color }]}>
      <Ionicons name={icon} size={22} color={color} />
      <Text style={sStat.value}>{value}</Text>
      <Text style={sStat.label}>{label}</Text>
    </View>
  );
}

function ActionCard({ icon, label, onPress }: { icon: any; label: string; onPress: () => void }) {
  return (
    <TouchableOpacity style={sAct.card} onPress={onPress}>
      <Ionicons name={icon} size={28} color={C.primary} />
      <Text style={sAct.label}>{label}</Text>
    </TouchableOpacity>
  );
}

const s = StyleSheet.create({
  container:       { flex: 1, backgroundColor: C.bg },
  hero:            { backgroundColor: C.primary, padding: 24, paddingTop: 32 },
  greeting:        { fontSize: 22, fontWeight: "800", color: C.white },
  sub:             { fontSize: 14, color: "#BFDBFE", marginTop: 4 },
  statsRow:        { flexDirection: "row", gap: 10, padding: 16 },
  sectionTitle:    { fontSize: 16, fontWeight: "700", color: C.textPrimary, paddingHorizontal: 16, marginTop: 8, marginBottom: 8 },
  inProgressBanner:{ flexDirection: "row", alignItems: "center", gap: 10, backgroundColor: "#FFFBEB", borderColor: C.warning, borderWidth: 1, margin: 16, borderRadius: 12, padding: 14 },
  inProgressText:  { flex: 1, color: C.textPrimary, fontSize: 13, fontWeight: "600" },
  actionsRow:      { flexDirection: "row", gap: 12, paddingHorizontal: 16, marginBottom: 8 },
  resultCard:      { flexDirection: "row", alignItems: "center", backgroundColor: C.card, marginHorizontal: 16, marginBottom: 8, borderRadius: 12, padding: 14, borderWidth: 1, borderColor: C.border },
  resultTitle:     { fontWeight: "600", color: C.textPrimary, fontSize: 14 },
  resultDate:      { fontSize: 12, color: C.textMuted, marginTop: 2 },
  scoreBadge:      { borderRadius: 8, paddingHorizontal: 10, paddingVertical: 6 },
  scoreText:       { color: C.white, fontWeight: "700", fontSize: 14 },
});
const sStat = StyleSheet.create({
  card:  { flex: 1, backgroundColor: C.card, borderRadius: 12, padding: 12, alignItems: "center", borderTopWidth: 3, borderColor: C.border, borderWidth: 1 },
  value: { fontSize: 20, fontWeight: "800", color: C.textPrimary, marginTop: 6 },
  label: { fontSize: 11, color: C.textMuted, marginTop: 2 },
});
const sAct = StyleSheet.create({
  card:  { flex: 1, backgroundColor: C.card, borderRadius: 14, padding: 20, alignItems: "center", gap: 8, borderWidth: 1, borderColor: C.border },
  label: { fontSize: 13, fontWeight: "600", color: C.textPrimary, textAlign: "center" },
});
