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

type Assessment = {
  id: number;
  title: string;
  description: string | null;
  total_marks: number;
  time_limit_min: number;
  subject: { name: string; code: string };
};

const SUBJECT_ICONS: Record<string, string> = {
  MATH: "calculator-outline",
  MLIT: "stats-chart-outline",
  PHSC: "flask-outline",
  PYDS: "code-slash-outline",
  CYBER: "shield-checkmark-outline",
};

export default function AssessmentsScreen() {
  const { token } = useAuth();
  const router = useRouter();
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [loading, setLoading]         = useState(true);
  const [refreshing, setRefreshing]   = useState(false);

  async function fetch_() {
    try {
      const res = await fetch(`${API_URL}/api/assessments/published`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) setAssessments(await res.json());
    } catch {} finally { setLoading(false); setRefreshing(false); }
  }

  useEffect(() => { fetch_(); }, []);

  if (loading) return <ActivityIndicator style={{ flex: 1 }} color={C.primary} />;

  return (
    <View style={s.container}>
      <FlatList
        data={assessments}
        keyExtractor={a => String(a.id)}
        contentContainerStyle={{ padding: 16, gap: 12 }}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); fetch_(); }} tintColor={C.primary} />}
        ListEmptyComponent={
          <View style={s.empty}>
            <Ionicons name="document-outline" size={48} color={C.textMuted} />
            <Text style={s.emptyText}>No assessments available yet.</Text>
          </View>
        }
        renderItem={({ item }) => (
          <TouchableOpacity
            style={s.card}
            onPress={() => router.push(`/assessment/${item.id}`)}
          >
            <View style={[s.iconBox, { backgroundColor: C.primaryLight }]}>
              <Ionicons
                name={(SUBJECT_ICONS[item.subject.code] ?? "document-text-outline") as any}
                size={24}
                color={C.primary}
              />
            </View>
            <View style={{ flex: 1 }}>
              <Text style={s.title} numberOfLines={2}>{item.title}</Text>
              <Text style={s.subject}>{item.subject.name}</Text>
              <View style={s.meta}>
                <Text style={s.metaText}>📝 {item.total_marks} marks</Text>
                <Text style={s.metaText}>⏱ {item.time_limit_min} min</Text>
              </View>
            </View>
            <Ionicons name="chevron-forward" size={18} color={C.textMuted} />
          </TouchableOpacity>
        )}
      />
    </View>
  );
}

const s = StyleSheet.create({
  container: { flex: 1, backgroundColor: C.bg },
  card:      { flexDirection: "row", alignItems: "center", gap: 14, backgroundColor: C.card, borderRadius: 14, padding: 16, borderWidth: 1, borderColor: C.border },
  iconBox:   { width: 48, height: 48, borderRadius: 12, alignItems: "center", justifyContent: "center" },
  title:     { fontSize: 14, fontWeight: "700", color: C.textPrimary, marginBottom: 2 },
  subject:   { fontSize: 12, color: C.primary, fontWeight: "600", marginBottom: 6 },
  meta:      { flexDirection: "row", gap: 12 },
  metaText:  { fontSize: 11, color: C.textSecondary },
  empty:     { alignItems: "center", marginTop: 80, gap: 12 },
  emptyText: { color: C.textMuted, fontSize: 14 },
});
