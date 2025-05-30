import React, { useState, useEffect } from 'react';
import {
  Container,
  Box,
  Typography,
  Button,
  Paper,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  Divider,
  TextField,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Alert,
  Snackbar,
} from '@mui/material';
import { Upload as UploadIcon, ExpandMore as ExpandMoreIcon, Code as CodeIcon } from '@mui/icons-material';
import * as api from './services/api';

function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState(null);
  const [versions, setVersions] = useState([]);
  const [showVersionDialog, setShowVersionDialog] = useState(false);
  const [versionName, setVersionName] = useState('');
  const [selectedVersions, setSelectedVersions] = useState([]);
  const [comparison, setComparison] = useState(null);
  const [userId] = useState('user_' + Math.random().toString(36).substr(2, 9));
  const [userInfo, setUserInfo] = useState({
    name: '',
    email: '',
    experience: '',
    targetRole: '',
    practiceQuestions: '',
    selectedQuestions: [],
  });
  const [devMode] = useState(process.env.REACT_APP_DEV_MODE === 'true');
  const [testDataCount, setTestDataCount] = useState(5);
  const [showDevPanel, setShowDevPanel] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });

  const interviewQuestions = {
    technical: {
      'Software Engineering': [
        'Explain the difference between REST and GraphQL',
        'How would you design a scalable database system?',
        'Explain the concept of microservices architecture',
        'How do you handle race conditions in concurrent programming?',
        'Explain the SOLID principles'
      ],
      'Data Science': [
        'Explain the difference between supervised and unsupervised learning',
        'How would you handle missing data in a dataset?',
        'Explain the concept of overfitting and how to prevent it',
        'Describe a time you used machine learning to solve a business problem',
        'How do you evaluate the performance of a model?'
      ],
      'Product Management': [
        'How do you prioritize features in a product roadmap?',
        'Describe your approach to user research',
        'How do you measure product success?',
        'Explain your process for gathering and implementing user feedback',
        'How do you handle competing stakeholder requirements?'
      ]
    },
    behavioral: [
      'Tell me about a time you faced a difficult challenge at work',
      'Describe a situation where you had to work with a difficult team member',
      'How do you handle tight deadlines and pressure?',
      'Tell me about a time you had to make a difficult decision',
      'Describe a project where you had to learn something new quickly'
    ],
    company: {
      'Google': [
        'How would you design a parking lot?',
        'Explain how you would implement a search engine',
        'How would you design a system to handle millions of concurrent users?'
      ],
      'Amazon': [
        'Tell me about a time you had to deal with ambiguity',
        'How do you handle customer complaints?',
        'Describe a time you had to make a data-driven decision'
      ],
      'Microsoft': [
        'How would you design a file system?',
        'Explain your approach to debugging complex issues',
        'How do you stay updated with new technologies?'
      ]
    }
  };

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
    setError(null);
  };

  const handleUserInfoChange = (field) => (event) => {
    setUserInfo({
      ...userInfo,
      [field]: event.target.value,
    });
  };

  const handleQuestionToggle = (question) => {
    setUserInfo(prev => ({
      ...prev,
      selectedQuestions: prev.selectedQuestions.includes(question)
        ? prev.selectedQuestions.filter(q => q !== question)
        : [...prev.selectedQuestions, question]
    }));
  };

  const showSnackbar = (message, severity = 'info') => {
    setSnackbar({ open: true, message, severity });
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  const handleUpload = async () => {
    if (!file) {
      showSnackbar('Please select a file first', 'error');
      return;
    }

    setLoading(true);
    try {
      const response = await api.analyzeResume(file);
      setAnalysis(response.data);
      showSnackbar('Resume analyzed successfully', 'success');
    } catch (err) {
      const errorMessage = err.response?.data?.error || 'An error occurred while analyzing the resume';
      showSnackbar(errorMessage, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveVersion = async () => {
    if (!file) return;
    
    try {
      await api.saveVersion(file, userId, versionName);
      setShowVersionDialog(false);
      setVersionName('');
      fetchVersions();
      showSnackbar('Version saved successfully', 'success');
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Failed to save version';
      showSnackbar(errorMessage, 'error');
    }
  };

  const fetchVersions = async () => {
    try {
      const response = await api.getVersions(userId);
      setVersions(response.data);
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Failed to fetch versions';
      showSnackbar(errorMessage, 'error');
    }
  };

  const handleCompareVersions = async () => {
    if (selectedVersions.length !== 2) return;
    
    try {
      const response = await api.compareVersions(selectedVersions[0], selectedVersions[1]);
      setComparison(response.data);
      showSnackbar('Versions compared successfully', 'success');
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Failed to compare versions';
      showSnackbar(errorMessage, 'error');
    }
  };

  const handleDeleteVersion = async (versionId) => {
    try {
      await api.deleteVersion(versionId);
      fetchVersions();
      showSnackbar('Version deleted successfully', 'success');
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Failed to delete version';
      showSnackbar(errorMessage, 'error');
    }
  };

  const handleGenerateTestData = async () => {
    try {
      await api.generateTestData(testDataCount);
      showSnackbar('Test data generated successfully', 'success');
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Failed to generate test data';
      showSnackbar(errorMessage, 'error');
    }
  };

  const handleClearTestData = async () => {
    try {
      await api.clearTestData();
      showSnackbar('Test data cleared successfully', 'success');
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Failed to clear test data';
      showSnackbar(errorMessage, 'error');
    }
  };

  useEffect(() => {
    fetchVersions();
  }, []);

  return (
    <Container maxWidth="md">
      <Box sx={{ my: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h3" component="h1" gutterBottom>
            Rate My Resume
          </Typography>
          {devMode && (
            <Button
              variant="outlined"
              color="secondary"
              startIcon={<CodeIcon />}
              onClick={() => setShowDevPanel(!showDevPanel)}
            >
              Dev Panel
            </Button>
          )}
        </Box>

        {devMode && showDevPanel && (
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h5" gutterBottom>
              Developer Panel
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  type="number"
                  label="Number of Test Versions"
                  value={testDataCount}
                  onChange={(e) => setTestDataCount(parseInt(e.target.value))}
                  inputProps={{ min: 1, max: 10 }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Box sx={{ display: 'flex', gap: 2 }}>
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={handleGenerateTestData}
                  >
                    Generate Test Data
                  </Button>
                  <Button
                    variant="outlined"
                    color="error"
                    onClick={handleClearTestData}
                  >
                    Clear Test Data
                  </Button>
                </Box>
              </Grid>
            </Grid>
          </Paper>
        )}

        <Paper sx={{ p: 3, mb: 3 }}>
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
            <input
              accept=".pdf"
              style={{ display: 'none' }}
              id="resume-upload"
              type="file"
              onChange={handleFileChange}
            />
            <label htmlFor="resume-upload">
              <Button
                variant="contained"
                component="span"
                startIcon={<UploadIcon />}
              >
                Select Resume
              </Button>
            </label>
            {file && (
              <Typography variant="body1">
                Selected: {file.name}
              </Typography>
            )}
            <Button
              variant="contained"
              color="primary"
              onClick={handleUpload}
              disabled={!file || loading}
            >
              {loading ? <CircularProgress size={24} /> : 'Analyze Resume'}
            </Button>
          </Box>
        </Paper>

        {error && (
          <Paper sx={{ p: 2, mb: 3, bgcolor: 'error.light' }}>
            <Typography color="error">{error}</Typography>
          </Paper>
        )}

        {analysis && (
          <Paper sx={{ p: 3, mb: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h4">
                Resume Score: {analysis.score}/100
              </Typography>
              <Button
                variant="contained"
                color="primary"
                onClick={() => setShowVersionDialog(true)}
              >
                Save Version
              </Button>
            </Box>
            
            <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
              Metrics
            </Typography>
            <List>
              <ListItem>
                <ListItemText
                  primary="Word Count"
                  secondary={analysis.metrics.word_count}
                />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="Sentence Count"
                  secondary={analysis.metrics.sentence_count}
                />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="Action Verbs Found"
                  secondary={analysis.metrics.action_verbs_found}
                />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="Technical Skills Found"
                  secondary={analysis.metrics.technical_skills_found}
                />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="Passive Voice Sentences"
                  secondary={analysis.metrics.passive_voice_sentences}
                />
              </ListItem>
            </List>

            <Divider sx={{ my: 2 }} />

            <Typography variant="h6" gutterBottom>
              Strengths
            </Typography>
            <List>
              {analysis.strengths.map((strength, index) => (
                <ListItem key={index}>
                  <ListItemText primary={strength} />
                </ListItem>
              ))}
            </List>

            <Typography variant="h6" gutterBottom>
              Areas for Improvement
            </Typography>
            <List>
              {analysis.weaknesses.map((weakness, index) => (
                <ListItem key={index}>
                  <ListItemText primary={weakness} />
                </ListItem>
              ))}
            </List>

            <Typography variant="h6" gutterBottom>
              Suggestions
            </Typography>
            <List>
              {analysis.suggestions.map((suggestion, index) => (
                <ListItem key={index}>
                  <ListItemText primary={suggestion} />
                </ListItem>
              ))}
            </List>
          </Paper>
        )}

        <Paper sx={{ p: 3 }}>
          <Typography variant="h5" gutterBottom>
            Your Information
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Name"
                value={userInfo.name}
                onChange={handleUserInfoChange('name')}
                margin="normal"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Email"
                type="email"
                value={userInfo.email}
                onChange={handleUserInfoChange('email')}
                margin="normal"
              />
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth margin="normal">
                <InputLabel>Years of Experience</InputLabel>
                <Select
                  value={userInfo.experience}
                  onChange={handleUserInfoChange('experience')}
                  label="Years of Experience"
                >
                  <MenuItem value="0-1">0-1 years</MenuItem>
                  <MenuItem value="1-3">1-3 years</MenuItem>
                  <MenuItem value="3-5">3-5 years</MenuItem>
                  <MenuItem value="5-10">5-10 years</MenuItem>
                  <MenuItem value="10+">10+ years</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Target Role"
                value={userInfo.targetRole}
                onChange={handleUserInfoChange('targetRole')}
                margin="normal"
                placeholder="e.g., Software Engineer, Product Manager"
              />
            </Grid>
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Practice Questions
              </Typography>
              <FormControl fullWidth margin="normal">
                <InputLabel>Question Category</InputLabel>
                <Select
                  value={userInfo.targetRole || ''}
                  onChange={handleUserInfoChange('targetRole')}
                  label="Question Category"
                >
                  <MenuItem value="Software Engineering">Software Engineering</MenuItem>
                  <MenuItem value="Data Science">Data Science</MenuItem>
                  <MenuItem value="Product Management">Product Management</MenuItem>
                </Select>
              </FormControl>
              
              {userInfo.targetRole && (
                <>
                  <Typography variant="subtitle1" sx={{ mt: 2, mb: 1 }}>
                    Technical Questions
                  </Typography>
                  <List>
                    {interviewQuestions.technical[userInfo.targetRole]?.map((question, index) => (
                      <ListItem key={`tech-${index}`}>
                        <ListItemText
                          primary={question}
                          secondary={
                            <Button
                              size="small"
                              onClick={() => handleQuestionToggle(question)}
                              color={userInfo.selectedQuestions.includes(question) ? "primary" : "default"}
                            >
                              {userInfo.selectedQuestions.includes(question) ? "Selected" : "Select"}
                            </Button>
                          }
                        />
                      </ListItem>
                    ))}
                  </List>

                  <Typography variant="subtitle1" sx={{ mt: 2, mb: 1 }}>
                    Behavioral Questions
                  </Typography>
                  <List>
                    {interviewQuestions.behavioral.map((question, index) => (
                      <ListItem key={`behav-${index}`}>
                        <ListItemText
                          primary={question}
                          secondary={
                            <Button
                              size="small"
                              onClick={() => handleQuestionToggle(question)}
                              color={userInfo.selectedQuestions.includes(question) ? "primary" : "default"}
                            >
                              {userInfo.selectedQuestions.includes(question) ? "Selected" : "Select"}
                            </Button>
                          }
                        />
                      </ListItem>
                    ))}
                  </List>

                  <Typography variant="subtitle1" sx={{ mt: 2, mb: 1 }}>
                    Company-Specific Questions
                  </Typography>
                  <List>
                    {Object.entries(interviewQuestions.company).map(([company, questions]) => (
                      <React.Fragment key={company}>
                        <Typography variant="subtitle2" sx={{ mt: 1, mb: 0.5 }}>
                          {company}
                        </Typography>
                        {questions.map((question, index) => (
                          <ListItem key={`${company}-${index}`}>
                            <ListItemText
                              primary={question}
                              secondary={
                                <Button
                                  size="small"
                                  onClick={() => handleQuestionToggle(question)}
                                  color={userInfo.selectedQuestions.includes(question) ? "primary" : "default"}
                                >
                                  {userInfo.selectedQuestions.includes(question) ? "Selected" : "Select"}
                                </Button>
                              }
                            />
                          </ListItem>
                        ))}
                      </React.Fragment>
                    ))}
                  </List>

                  <Typography variant="subtitle1" sx={{ mt: 2, mb: 1 }}>
                    Selected Questions ({userInfo.selectedQuestions.length})
                  </Typography>
                  <List>
                    {userInfo.selectedQuestions.map((question, index) => (
                      <ListItem key={`selected-${index}`}>
                        <ListItemText primary={question} />
                      </ListItem>
                    ))}
                  </List>
                </>
              )}
            </Grid>
            <Grid item xs={12}>
              <Button
                variant="contained"
                color="primary"
                fullWidth
                onClick={() => console.log('User info:', userInfo)}
              >
                Save Information
              </Button>
            </Grid>
          </Grid>
        </Paper>

        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h5" gutterBottom>
            Resume Versions
          </Typography>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Version Name</TableCell>
                  <TableCell>Score</TableCell>
                  <TableCell>Date</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {versions.map((version) => (
                  <TableRow key={version.id}>
                    <TableCell>{version.version_name}</TableCell>
                    <TableCell>{version.score}</TableCell>
                    <TableCell>
                      {new Date(version.created_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Button
                          size="small"
                          onClick={() => {
                            setSelectedVersions(prev => {
                              const newSelection = prev.includes(version.id)
                                ? prev.filter(id => id !== version.id)
                                : [...prev, version.id].slice(-2);
                              return newSelection;
                            });
                          }}
                          color={selectedVersions.includes(version.id) ? "secondary" : "primary"}
                        >
                          {selectedVersions.includes(version.id) ? "Deselect" : "Select for Compare"}
                        </Button>
                        <Button
                          size="small"
                          color="error"
                          onClick={() => {
                            if (window.confirm('Are you sure you want to delete this version?')) {
                              handleDeleteVersion(version.id);
                            }
                          }}
                        >
                          Delete
                        </Button>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          
          {selectedVersions.length === 2 && (
            <Box sx={{ mt: 2 }}>
              <Button
                variant="contained"
                color="primary"
                onClick={handleCompareVersions}
              >
                Compare Selected Versions
              </Button>
            </Box>
          )}
        </Paper>

        {comparison && (
          <Paper sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>
              Version Comparison
            </Typography>
            <List>
              <ListItem>
                <ListItemText
                  primary="Score Difference"
                  secondary={`${comparison.score_difference > 0 ? '+' : ''}${comparison.score_difference.toFixed(1)}`}
                />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="Time Between Versions"
                  secondary={`${Math.round(comparison.created_at_difference / 86400)} days`}
                />
              </ListItem>
              <Divider />
              <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>
                Section Changes
              </Typography>
              {Object.entries(comparison.section_changes).map(([section, change]) => (
                <ListItem key={section}>
                  <ListItemText
                    primary={section}
                    secondary={change}
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
        )}

        <Dialog open={showVersionDialog} onClose={() => setShowVersionDialog(false)}>
          <DialogTitle>Save Resume Version</DialogTitle>
          <DialogContent>
            <TextField
              autoFocus
              margin="dense"
              label="Version Name"
              fullWidth
              value={versionName}
              onChange={(e) => setVersionName(e.target.value)}
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setShowVersionDialog(false)}>Cancel</Button>
            <Button onClick={handleSaveVersion} color="primary">
              Save
            </Button>
          </DialogActions>
        </Dialog>

        <Snackbar
          open={snackbar.open}
          autoHideDuration={6000}
          onClose={handleCloseSnackbar}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        >
          <Alert onClose={handleCloseSnackbar} severity={snackbar.severity}>
            {snackbar.message}
          </Alert>
        </Snackbar>
      </Box>
    </Container>
  );
}

export default App; 