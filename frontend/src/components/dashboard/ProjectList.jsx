import { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { projectsAPI } from '../../services/api';
import {
  Box, Button, Grid, Heading, Card, CardBody, CardHeader,
  Badge, Text, IconButton, HStack, useToast, Spinner, Center,
  AlertDialog, AlertDialogBody, AlertDialogFooter, AlertDialogHeader,
  AlertDialogContent, AlertDialogOverlay, useDisclosure
} from '@chakra-ui/react';
import { AddIcon, EditIcon, DeleteIcon } from '@chakra-ui/icons';
import { format } from 'date-fns';

export const ProjectList = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [deleteId, setDeleteId] = useState(null);
  const { isOpen, onOpen, onClose } = useDisclosure();
  const cancelRef = useRef();
  const navigate = useNavigate();
  const toast = useToast();

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      const response = await projectsAPI.list();
      setProjects(response.data);
    } catch (error) {
      toast({
        title: 'Failed to load projects',
        description: error.response?.data?.detail || 'Unable to fetch projects',
        status: 'error',
        duration: 3000,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteClick = (projectId) => {
    setDeleteId(projectId);
    onOpen();
  };

  const handleDeleteConfirm = async () => {
    try {
      await projectsAPI.delete(deleteId);
      toast({
        title: 'Project deleted',
        status: 'success',
        duration: 2000,
      });
      loadProjects();
    } catch (error) {
      toast({
        title: 'Delete failed',
        description: error.response?.data?.detail || 'Unable to delete project',
        status: 'error',
        duration: 3000,
      });
    } finally {
      onClose();
      setDeleteId(null);
    }
  };

  if (loading) {
    return (
      <Center h="80vh">
        <Spinner size="xl" color="blue.500" />
      </Center>
    );
  }

  return (
    <Box p={8}>
      <HStack justify="space-between" mb={6}>
        <Heading>My Projects</Heading>
        <Button
          leftIcon={<AddIcon />}
          colorScheme="blue"
          onClick={() => navigate('/create')}
        >
          New Project
        </Button>
      </HStack>

      {projects.length === 0 ? (
        <Center py={20}>
          <Box textAlign="center">
            <Heading size="md" color="gray.500" mb={4}>
              No projects yet
            </Heading>
            <Text color="gray.400" mb={6}>
              Create your first AI-powered document!
            </Text>
            <Button
              colorScheme="blue"
              onClick={() => navigate('/create')}
            >
              Get Started
            </Button>
          </Box>
        </Center>
      ) : (
        <Grid templateColumns="repeat(auto-fill, minmax(320px, 1fr))" gap={6}>
          {projects.map((project) => (
            <Card
              key={project.id}
              cursor="pointer"
              _hover={{ shadow: 'lg', transform: 'translateY(-2px)' }}
              transition="all 0.2s"
              onClick={() => navigate(`/editor/${project.id}`)}
            >
              <CardHeader>
                <HStack justify="space-between">
                  <Heading size="md" noOfLines={1}>
                    {project.title}
                  </Heading>
                  <Badge
                    colorScheme={project.doc_type === 'docx' ? 'blue' : 'orange'}
                    fontSize="sm"
                  >
                    {project.doc_type.toUpperCase()}
                  </Badge>
                </HStack>
              </CardHeader>
              <CardBody>
                <Text fontSize="sm" color="gray.600" noOfLines={2} mb={3}>
                  {project.topic}
                </Text>
                <Text fontSize="xs" color="gray.400" mb={4}>
                  {project.sections?.length || 0}{' '}
                  {project.doc_type === 'docx' ? 'sections' : 'slides'} •{' '}
                  Updated {format(new Date(project.updated_at), 'MMM d, yyyy')}
                </Text>
                <HStack spacing={2} onClick={(e) => e.stopPropagation()}>
                  <IconButton
                    icon={<EditIcon />}
                    size="sm"
                    colorScheme="blue"
                    variant="outline"
                    onClick={(e) => {
                      e.stopPropagation();
                      navigate(`/editor/${project.id}`);
                    }}
                  />
                  <IconButton
                    icon={<DeleteIcon />}
                    size="sm"
                    colorScheme="red"
                    variant="outline"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteClick(project.id);
                    }}
                  />
                </HStack>
              </CardBody>
            </Card>
          ))}
        </Grid>
      )}

      <AlertDialog
        isOpen={isOpen}
        leastDestructiveRef={cancelRef}
        onClose={onClose}
      >
        <AlertDialogOverlay>
          <AlertDialogContent>
            <AlertDialogHeader fontSize="lg" fontWeight="bold">
              Delete Project
            </AlertDialogHeader>
            <AlertDialogBody>
              Are you sure? This action cannot be undone.
            </AlertDialogBody>
            <AlertDialogFooter>
              <Button ref={cancelRef} onClick={onClose}>
                Cancel
              </Button>
              <Button colorScheme="red" onClick={handleDeleteConfirm} ml={3}>
                Delete
              </Button>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialogOverlay>
      </AlertDialog>
    </Box>
  );
};
