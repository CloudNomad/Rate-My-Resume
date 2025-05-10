import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Share,
} from 'react-native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { RouteProp } from '@react-navigation/native';
import { RootStackParamList } from '../../App';
import Icon from 'react-native-vector-icons/MaterialIcons';

type ResultsScreenProps = {
  navigation: NativeStackNavigationProp<RootStackParamList, 'Results'>;
  route: RouteProp<RootStackParamList, 'Results'>;
};

export default function ResultsScreen({ route }: ResultsScreenProps) {
  const { analysisData } = route.params;

  const shareResults = async () => {
    try {
      const message = `My Resume Score: ${analysisData.score}/100\n\n` +
        `Strengths:\n${analysisData.strengths.join('\n')}\n\n` +
        `Areas for Improvement:\n${analysisData.weaknesses.join('\n')}\n\n` +
        `Suggestions:\n${analysisData.suggestions.join('\n')}`;

      await Share.share({
        message,
        title: 'My Resume Analysis Results',
      });
    } catch (error) {
      console.error('Error sharing results:', error);
    }
  };

  const renderSection = (title: string, data: any) => (
    <View style={styles.section}>
      <Text style={styles.sectionTitle}>{title}</Text>
      {Array.isArray(data) ? (
        data.map((item, index) => (
          <View key={index} style={styles.listItem}>
            <Icon name="check-circle" size={20} color="#4CAF50" />
            <Text style={styles.listItemText}>{item}</Text>
          </View>
        ))
      ) : (
        Object.entries(data).map(([key, value]) => (
          <View key={key} style={styles.detailItem}>
            <Text style={styles.detailLabel}>{key}:</Text>
            <Text style={styles.detailValue}>{JSON.stringify(value)}</Text>
          </View>
        ))
      )}
    </View>
  );

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <View style={styles.scoreContainer}>
          <Text style={styles.score}>{analysisData.score}</Text>
          <Text style={styles.scoreLabel}>Overall Score</Text>
        </View>
        <TouchableOpacity style={styles.shareButton} onPress={shareResults}>
          <Icon name="share" size={24} color="#fff" />
          <Text style={styles.shareButtonText}>Share Results</Text>
        </TouchableOpacity>
      </View>

      {renderSection('Strengths', analysisData.strengths)}
      {renderSection('Areas for Improvement', analysisData.weaknesses)}
      {renderSection('Suggestions', analysisData.suggestions)}

      {Object.entries(analysisData.sections).map(([section, data]: [string, any]) => (
        <View key={section} style={styles.section}>
          <Text style={styles.sectionTitle}>{section.charAt(0).toUpperCase() + section.slice(1)}</Text>
          <View style={styles.sectionScore}>
            <Text style={styles.sectionScoreText}>Score: {data.score}</Text>
          </View>
          {data.suggestions.map((suggestion: string, index: number) => (
            <View key={index} style={styles.listItem}>
              <Icon name="lightbulb" size={20} color="#FFC107" />
              <Text style={styles.listItemText}>{suggestion}</Text>
            </View>
          ))}
        </View>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: '#2196F3',
    padding: 20,
    alignItems: 'center',
  },
  scoreContainer: {
    alignItems: 'center',
    marginBottom: 20,
  },
  score: {
    fontSize: 48,
    fontWeight: 'bold',
    color: '#fff',
  },
  scoreLabel: {
    fontSize: 16,
    color: '#fff',
    opacity: 0.8,
  },
  shareButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
  },
  shareButtonText: {
    color: '#fff',
    marginLeft: 8,
    fontSize: 16,
  },
  section: {
    backgroundColor: '#fff',
    margin: 10,
    padding: 15,
    borderRadius: 8,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
  },
  sectionScore: {
    backgroundColor: '#E3F2FD',
    padding: 8,
    borderRadius: 4,
    marginBottom: 10,
  },
  sectionScoreText: {
    color: '#1976D2',
    fontWeight: '600',
  },
  listItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 4,
  },
  listItemText: {
    marginLeft: 8,
    fontSize: 16,
    color: '#333',
    flex: 1,
  },
  detailItem: {
    flexDirection: 'row',
    marginVertical: 4,
  },
  detailLabel: {
    fontWeight: 'bold',
    color: '#666',
    marginRight: 8,
  },
  detailValue: {
    color: '#333',
    flex: 1,
  },
}); 