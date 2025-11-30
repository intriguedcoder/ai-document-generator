import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { projectsAPI, exportAPI } from '../../services/api';
import {
  Box, Button, VStack, HStack, Heading, useToast,
  Spinner, Center, Badge, Divider
} from '@chakra-ui/react';
import { DownloadIcon, ArrowBackIcon } from '@chakra-ui/icons';
import { SectionCard } from './SectionCard';

export const DocumentEditor = () => {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);
  const toast = useToast();

  useEffect(() => {
    loadProject();
  }, [projectId]);

  const loadProject = async () => {
    try {
      const response = await projectsAPI.get(projectId);
      setProject(response.data);
    } catch (error) {
      toast({
        title: 'Failed to load project',
        description: error.response?.data?.detail,
        status: 'error',
        duration: 3000,
      });
      navigate('/dashboard');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    setExporting(true);
    try {
      const exportFunc = project.doc_type === 'docx' 
        ? exportAPI.docx 
        : exportAPI.pptx;
      
      const response = await exportFunc(projectId);

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute(
        'download',
        `${project.title}.${project.doc_type}`
      );
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      toast({
        title: 'Document exported successfully!',
        description: `${project.title}.${project.doc_type} downloaded`,
        status: 'success',
        duration: 3000,
      });
    } catch (error) {
      toast({
        title: 'Export failed',
        description: error.response?.data?.detail || 'Unable to export document',
        status: 'error',
        duration: 3000,
      });
    } finally {
      setExporting(false);
    }
  };

  const handleSave = async () => {
    try {
      await projectsAPI.update(projectId, {
        sections: project.sections
      });
      
      toast({
        title: 'Project saved',
        status: 'success',
        duration: 2000,
      });
    } catch (error) {
      toast({
        title: 'Save failed',
        status: 'error',
        duration: 2000,
      });
    }
  };

  if (loading) {
    return (
      <Center h="80vh">
        <Spinner size="xl" color="blue.500" />
      </Center>
    );
  }

  if (!project) return null;

  return (
    <Box p={8} maxW="10xl" mx="auto">
      <VStack spacing={4} align="stretch" mb={6}>
        <HStack justify="space-between">
          <HStack>
            <Button
              leftIcon={<ArrowBackIcon />}
              variant="ghost"
              onClick={() => navigate('/dashboard')}
            >
              Back to Projects
            </Button>
          </HStack>
          <HStack>
            <Button onClick={handleSave} colorScheme="green">
              Save Changes
            </Button>
            <Button
              onClick={handleExport}
              leftIcon={<DownloadIcon />}
              colorScheme="blue"
              isLoading={exporting}
              loadingText="Exporting..."
            >
              Export {project.doc_type.toUpperCase()}
            </Button>
          </HStack>
        </HStack>

        <HStack justify="space-between" align="start">
          <VStack align="start" spacing={2}>
            <Heading size="xl">{project.title}</Heading>
            <HStack>
              <Badge colorScheme={project.doc_type === 'docx' ? 'blue' : 'orange'}>
                {project.doc_type.toUpperCase()}
              </Badge>
              <Badge colorScheme="gray">
                {project.sections?.length || 0}{' '}
                {project.doc_type === 'docx' ? 'sections' : 'slides'}
              </Badge>
            </HStack>
          </VStack>
        </HStack>

        <Box p={4} bg="blue.50" borderRadius="md" borderLeftWidth={4} borderLeftColor="blue.500">
          <Heading size="sm" mb={1}>Topic:</Heading>
          <Box color="gray.700">{project.topic}</Box>
        </Box>
      </VStack>

      <Divider mb={6} />

      {project.sections && project.sections.length > 0 ? (
        <VStack spacing={6} align="stretch">
          {project.sections
            .sort((a, b) => a.order - b.order)
            .map((section) => (
              <SectionCard
                key={section.id}
                section={section}
                projectId={projectId}
                projectTopic={project.topic}
                onUpdate={loadProject}
              />
            ))}
        </VStack>
      ) : (
        <Center py={20}>
          <Box textAlign="center">
            <Heading size="md" color="gray.500">
              No sections defined
            </Heading>
            <Button
              mt={4}
              colorScheme="blue"
              onClick={() => navigate('/dashboard')}
            >
              Go Back
            </Button>
          </Box>
        </Center>
      )}
    </Box>
  );
};
