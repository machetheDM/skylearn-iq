import React, { useEffect, useState } from "react";
import {
  View, Text, FlatList, TouchableOpacity,
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
  score: { total_marks_awarded: number; total_marks_possible: number; percentage: number; pass_fail: boolean | null } | null;
};

export default function ResultsScreen() {
  const { token } = useAuth();
  const router = useRouter();
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading]   = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  async function fetch_() {
    try {
      const res = await fetch(`${API_URL}/api/sessions/learner/my-sessions`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) setSessions(await res.json());
    } catch {} finally { setLoading(false); setRefreshing(false); }
  }

  useEffect(() => { fetch_(); }, []);

  const completed = sessions.filter(s => s.status === "COMPLETED");

  if (loading) return <ActivityIndicator style={{ flex: 1 }} color={C.primary} />;

  return (
    <View style={s.container}>
      <FlatList
        data={completed}
        keyExtractor={item => String(item.id)}
        contentContainerStyle={{ padding: 16, gap: 10 }}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); fetch_(); }} tintColor={C.primary} />}
        ListEmptyComponent={
          <View style={s.empty}>
            <Ionicons name="bar-chart-outline" size={48} color={C.textMuted} />
            <Text style={s.emptyText}>No results yet. Complete an assessment first!</Text>
          </View>
        }
        renderItem={({ item }) => {
          const pct  = Math.round(item.score?.percentage ?? 0);
          const pass = item.score?.pass_fail;
          const color = pass === true ? C.accent : pass === false ? C.danger : C.textMuted;
          return (
            <TouchableOpacity style={s.card} onPress={() => router.push(`/assessment/result/${item.id}`)}>
              <View style={[s.scoreBubble, { backgroundColor: color }]}>
                <Text style={s.scoreNum}>{pct}%</Text>
              </View>
              <View style={{ flex: 1 }}>
                <Text style={s.title}>Assessment #{item.assessment_id}</Text>
                <Text style={s.meta}>
                  {item.score?.total_marks_awarded ?? 0}/{item.score?.total_marks_possible ?? 0} marks
                  {" · "}
                  {pass === true ? "✅ Pass" : pass === false ? "❌ Fail" : "—"}
                </Text>
                <Text style={s.date}>{new Date(item.completed_at!).toLocaleDateString("en-ZA")}</Text>
              </View>
              <Ionicons name="chevron-forward" size={16} color={C.textMuted} />
            </TouchableOpacity>
          );
        }}
      />
    </View>
  );
}

const s = StyleSheet.create({
  container:   { flex: 1, backgroundColor: C.bg },
  card:        { flexDirection: "row", alignItems: "center", gap: 14, backgroundColor: C.card, borderRadius: 14, padding: 14, borderWidth: 1, borderColor: C.border },
  scoreBubble: { width: 56, height: 56, borderRadius: 28, alignItems: "center", justifyContent: "center" },
  scoreNum:    { color: C.white, fontWeight: "800", fontSize: 15 },
  title:       { fontWeight: "700", color: C.textPrimary, fontSize: 14 },
  meta:        { fontSize: 12, color: C.textSecondary, marginTop: 2 },
  date:        { fontSize: 11, color: C.textMuted, marginTop: 2 },
  empty:       { alignItems: "center", marginTop: 80, gap: 12 },
  emptyText:   { color: C.textMuted, fontSize: 14, textAlign: "center", paddingHorizontal: 32 },
});
