import { useState } from 'react';
import {
  Box, Button, FormControl, FormLabel, Input, Textarea,
  VStack, HStack, Radio, RadioGroup, Stack, useToast, Heading,
  Card, CardBody, IconButton, Text, Badge, Radio as ChakraRadio
} from '@chakra-ui/react';
import { AddIcon, DeleteIcon, CheckIcon } from '@chakra-ui/icons';
import { useNavigate } from 'react-router-dom';
import { projectsAPI, generateAPI } from '../../services/api';

const RadioComp = ChakraRadio; // alias to avoid JSX confusion if needed

export const ProjectConfig = () => {
  const [step, setStep] = useState(1);
  const [title, setTitle] = useState('');
  const [docType, setDocType] = useState('docx');
  const [topic, setTopic] = useState('');
  const [description, setDescription] = useState('');
  const [sections, setSections] = useState([]);
  const [numSections, setNumSections] = useState(5);
  const [isGeneratingOutline, setIsGeneratingOutline] = useState(false);
  const [aiOutline, setAiOutline] = useState(null);
  
  const toast = useToast();
  const navigate = useNavigate();

  const handleAIOutline = async () => {
    if (!topic.trim()) {
      toast({
        title: 'Enter a topic first',
        status: 'warning',
        duration: 2000,
      });
      return;
    }

    setIsGeneratingOutline(true);
    try {
      const response = await generateAPI.outline({
        topic: topic,
        doc_type: docType,
        num_sections: numSections
      });

      setAiOutline(response.data);
      const aiSections = response.data.sections.map((section, index) => ({
        id: `section-${Date.now()}-${index}`,
        title: section.title,
        description: section.description || section.content_points?.join('. ') || '',
        order: index + 1,
        content: ''
      }));
      setSections(aiSections);

      toast({
        title: 'AI outline generated!',
        description: `${aiSections.length} sections suggested`,
        status: 'success',
        duration: 3000,
      });
    } catch (error) {
      toast({
        title: 'Generation failed',
        description: error.response?.data?.detail || 'Unable to generate outline',
        status: 'error',
        duration: 3000,
      });
    } finally {
      setIsGeneratingOutline(false);
    }
  };

  const handleAddSection = () => {
    setSections([
      ...sections,
      {
        id: `section-${Date.now()}`,
        title: '',
        description: '',
        order: sections.length + 1,
        content: ''
      }
    ]);
  };

  const handleRemoveSection = (id) => {
    setSections(sections.filter(s => s.id !== id));
  };

  const handleSectionChange = (id, field, value) => {
    setSections(sections.map(s => 
      s.id === id ? { ...s, [field]: value } : s
    ));
  };

  const handleCreateProject = async () => {
    if (sections.length === 0) {
      toast({
        title: 'Add at least one section',
        status: 'warning',
        duration: 2000,
      });
      return;
    }

    const invalidSections = sections.filter(s => !s.title.trim());
    if (invalidSections.length > 0) {
      toast({
        title: 'All sections must have titles',
        status: 'warning',
        duration: 2000,
      });
      return;
    }

    try {
      const projectData = {
        title,
        doc_type: docType,
        topic,
        description,
        sections: sections.map((s, idx) => ({
          title: s.title,
          content: s.content,
          order: idx + 1
        }))
      };

      const response = await projectsAPI.create(projectData);
      
      toast({
        title: 'Project created!',
        status: 'success',
        duration: 2000,
      });

      navigate(`/editor/${response.data.id}`);
    } catch (error) {
      toast({
        title: 'Failed to create project',
        description: error.response?.data?.detail,
        status: 'error',
        duration: 3000,
      });
    }
  };

  return (
    <Box w="100%" py={8}>
      <VStack spacing={8} align="stretch">
        <Heading>Create New Document</Heading>

        {step === 1 && (
          <Card>
            <CardBody>
              <VStack spacing={6} align="stretch">
                <Heading size="md">Step 1: Document Configuration</Heading>

                <FormControl isRequired>
                  <FormLabel>Document Type</FormLabel>
                  <RadioGroup 
                    value={docType} 
                    onChange={(value) => {
                      setDocType(value);
                      setSections([]);
                      setAiOutline(null);
                    }}
                  >
                    <Stack direction="row" spacing={4}>
                      <RadioComp value="docx">Word Document (.docx)</RadioComp>
                      <RadioComp value="pptx">PowerPoint (.pptx)</RadioComp>
                    </Stack>
                  </RadioGroup>
                </FormControl>

                <FormControl isRequired>
                  <FormLabel>Document Title</FormLabel>
                  <Input
                    placeholder="e.g., Market Analysis Report 2025"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                  />
                </FormControl>

                <FormControl isRequired>
                  <FormLabel>Main Topic / Prompt</FormLabel>
                  <Textarea
                    placeholder="Describe the main topic or purpose of your document..."
                    value={topic}
                    onChange={(e) => setTopic(e.target.value)}
                    rows={4}
                  />
                </FormControl>

                <FormControl>
                  <FormLabel>Description (Optional)</FormLabel>
                  <Textarea
                    placeholder="Additional context or requirements..."
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    rows={3}
                  />
                </FormControl>

                <Button
                  colorScheme="blue"
                  onClick={() => setStep(2)}
                  isDisabled={!title.trim() || !topic.trim()}
                >
                  Next: Define Structure
                </Button>
              </VStack>
            </CardBody>
          </Card>
        )}

        {step === 2 && (
          <>
            <Card bg="purple.50">
              <CardBody>
                <VStack spacing={4} align="stretch">
                  <Heading size="md" color="purple.700">
                    ✨ AI-Suggest Outline (BONUS)
                  </Heading>
                  <Text>
                    Let AI suggest a complete {docType === 'docx' ? 'document' : 'presentation'} structure based on your topic.
                  </Text>
                  
                  <HStack>
                    <FormControl maxW="200px">
                      <FormLabel>Number of {docType === 'docx' ? 'Sections' : 'Slides'}</FormLabel>
                      <Input
                        type="number"
                        min="3"
                        max="10"
                        value={numSections}
                        onChange={(e) => setNumSections(parseInt(e.target.value))}
                      />
                    </FormControl>
                    <Button
                      colorScheme="purple"
                      onClick={handleAIOutline}
                      isLoading={isGeneratingOutline}
                      loadingText="Generating..."
                      mt={8}
                    >
                      Generate Outline with AI
                    </Button>
                  </HStack>
                </VStack>
              </CardBody>
            </Card>

            <Card>
              <CardBody>
                <VStack spacing={6} align="stretch">
                  <HStack justify="space-between">
                    <Heading size="md">
                      Step 2: Define {docType === 'docx' ? 'Sections' : 'Slides'}
                    </Heading>
                    <Badge colorScheme="blue">
                      {sections.length} {docType === 'docx' ? 'sections' : 'slides'}
                    </Badge>
                  </HStack>

                  {sections.map((section, index) => (
                    <Card key={section.id} variant="outline">
                      <CardBody>
                        <VStack spacing={3} align="stretch">
                          <HStack justify="space-between">
                            <Heading size="sm">
                              {docType === 'docx' ? 'Section' : 'Slide'} {index + 1}
                            </Heading>
                            <IconButton
                              icon={<DeleteIcon />}
                              size="sm"
                              colorScheme="red"
                              variant="ghost"
                              onClick={() => handleRemoveSection(section.id)}
                            />
                          </HStack>

                          <FormControl isRequired>
                            <FormLabel>Title</FormLabel>
                            <Input
                              value={section.title}
                              onChange={(e) => handleSectionChange(section.id, 'title', e.target.value)}
                              placeholder={`${docType === 'docx' ? 'Section' : 'Slide'} title...`}
                            />
                          </FormControl>

                          <FormControl>
                            <FormLabel>Description</FormLabel>
                            <Textarea
                              value={section.description}
                              onChange={(e) => handleSectionChange(section.id, 'description', e.target.value)}
                              placeholder="Brief description of what this covers..."
                              rows={2}
                            />
                          </FormControl>
                        </VStack>
                      </CardBody>
                    </Card>
                  ))}

                  <Button
                    leftIcon={<AddIcon />}
                    onClick={handleAddSection}
                    variant="outline"
                  >
                    Add {docType === 'docx' ? 'Section' : 'Slide'} Manually
                  </Button>

                  <HStack spacing={4}>
                    <Button onClick={() => setStep(1)} variant="outline">
                      Back
                    </Button>
                    <Button
                      colorScheme="green"
                      onClick={handleCreateProject}
                      leftIcon={<CheckIcon />}
                      isDisabled={sections.length === 0}
                    >
                      Create Project & Start Editing
                    </Button>
                  </HStack>
                </VStack>
              </CardBody>
            </Card>
          </>
        )}
      </VStack>
    </Box>
  );
};
