import { useState } from 'react';
import {
  Box, Button, Card, CardBody, CardHeader, Heading, HStack,
  VStack, Textarea, Input, IconButton, Badge, useToast, Collapse, Text
} from '@chakra-ui/react';
import {
  EditIcon, CheckIcon, CloseIcon, RepeatIcon
} from '@chakra-ui/icons';
import { DiffViewer } from './DiffViewer';
import { VersionHistory } from './VersionHistory';
import { generateAPI, refineAPI } from '../../services/api';

export const SectionCard = ({ section, projectId, projectTopic, onUpdate }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editedTitle, setEditedTitle] = useState(section.title);
  const [editedContent, setEditedContent] = useState(section.content);
  const [refinementPrompt, setRefinementPrompt] = useState('');
  const [comment, setComment] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [isRefining, setIsRefining] = useState(false);
  const [showDiff, setShowDiff] = useState(false);
  const [diffData, setDiffData] = useState(null);
  const toast = useToast();

  const handleGenerate = async () => {
    setIsGenerating(true);
    try {
      const response = await generateAPI.content({
        project_id: projectId,
        section_id: section.id,
        context: projectTopic,
        tone: 'professional'
      });

      setEditedContent(response.data.content);
      onUpdate();
      
      toast({
        title: 'Content generated!',
        status: 'success',
        duration: 2000,
      });
    } catch (error) {
      toast({
        title: 'Generation failed',
        description: error.response?.data?.detail,
        status: 'error',
        duration: 3000,
      });
    } finally {
      setIsGenerating(false);
    }
  };

  const handleRefine = async () => {
    if (!refinementPrompt.trim()) {
      toast({
        title: 'Enter refinement instructions',
        status: 'warning',
        duration: 2000,
      });
      return;
    }

    setIsRefining(true);
    try {
      const response = await refineAPI.refine({
        project_id: projectId,
        section_id: section.id,
        refinement_prompt: refinementPrompt
      });

      setEditedContent(response.data.content);
      setDiffData({
        original: section.content,
        refined: response.data.content
      });
      setShowDiff(true);
      setRefinementPrompt('');
      onUpdate();

      toast({
        title: 'Content refined!',
        description: `Version ${response.data.version} created`,
        status: 'success',
        duration: 2000,
      });
    } catch (error) {
      toast({
        title: 'Refinement failed',
        description: error.response?.data?.detail,
        status: 'error',
        duration: 3000,
      });
    } finally {
      setIsRefining(false);
    }
  };

  const handleFeedback = async (feedback) => {
    try {
      await refineAPI.feedback({
        project_id: projectId,
        section_id: section.id,
        version: section.versions?.length || 1,
        feedback: feedback, // Can be 'like', 'dislike', or null (for comment-only)
        comment: comment
      });

      toast({
        title: feedback ? 'Feedback saved' : 'Comment saved',
        status: 'success',
        duration: 2000,
      });
      setComment('');
      onUpdate();
    } catch (error) {
      toast({
        title: 'Failed to save feedback',
        status: 'error',
        duration: 2000,
      });
    }
  };

  const handleCommentSave = () => {
    if (comment.trim()) {
      handleFeedback(null); // Save comment without like/dislike
    }
  };

  const handleRevert = async (version) => {
    try {
      await refineAPI.revert({
        project_id: projectId,
        section_id: section.id,
        target_version: version
      });

      toast({
        title: 'Reverted successfully',
        status: 'success',
        duration: 2000,
      });
      onUpdate();
    } catch (error) {
      toast({
        title: 'Revert failed',
        status: 'error',
        duration: 2000,
      });
    }
  };

  const handleSaveEdit = () => {
    section.title = editedTitle;
    section.content = editedContent;
    setIsEditing(false);
    onUpdate();
  };

  return (
    <Card mb={4} shadow="md">
      <CardHeader bg="gray.50">
        <HStack justify="space-between">
          {isEditing ? (
            <Input
              value={editedTitle}
              onChange={(e) => setEditedTitle(e.target.value)}
              size="lg"
              fontWeight="bold"
            />
          ) : (
            <Heading size="md">{section.title}</Heading>
          )}

          <HStack>
            <Badge colorScheme="purple">
              {section.versions?.length || 0} versions
            </Badge>
            {isEditing ? (
              <>
                <IconButton
                  icon={<CheckIcon />}
                  colorScheme="green"
                  size="sm"
                  onClick={handleSaveEdit}
                />
                <IconButton
                  icon={<CloseIcon />}
                  size="sm"
                  onClick={() => {
                    setIsEditing(false);
                    setEditedTitle(section.title);
                    setEditedContent(section.content);
                  }}
                />
              </>
            ) : (
              <IconButton
                icon={<EditIcon />}
                size="sm"
                onClick={() => setIsEditing(true)}
              />
            )}
          </HStack>
        </HStack>
      </CardHeader>

      <CardBody>
        <VStack spacing={4} align="stretch">
          {/* Content Display/Edit */}
          {isEditing ? (
            <Textarea
              value={editedContent}
              onChange={(e) => setEditedContent(e.target.value)}
              minH="200px"
              placeholder="Section content..."
            />
          ) : (
            <Box
              p={4}
              bg="gray.50"
              borderRadius="md"
              minH="150px"
              whiteSpace="pre-wrap"
            >
              {section.content || (
                <Text color="gray.400" fontStyle="italic">
                  No content yet. Generate content to get started.
                </Text>
              )}
            </Box>
          )}

          {/* Generate Button */}
          {!section.content && (
            <Button
              colorScheme="green"
              onClick={handleGenerate}
              isLoading={isGenerating}
              loadingText="Generating..."
              leftIcon={<RepeatIcon />}
            >
              Generate Content with AI
            </Button>
          )}

          {/* Refinement Interface */}
          {section.content && (
            <VStack spacing={3} align="stretch">
              <Heading size="sm" color="gray.600">
                AI Refinement
              </Heading>
              <HStack>
                <Input
                  placeholder="e.g., 'Make more formal' or 'Add statistics'"
                  value={refinementPrompt}
                  onChange={(e) => setRefinementPrompt(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleRefine()}
                />
                <Button
                  colorScheme="purple"
                  onClick={handleRefine}
                  isLoading={isRefining}
                  loadingText="Refining..."
                >
                  Refine
                </Button>
              </HStack>

              {/* Diff Viewer */}
              <Collapse in={showDiff}>
                {diffData && (
                  <DiffViewer
                    original={diffData.original}
                    refined={diffData.refined}
                  />
                )}
              </Collapse>

              {/* Feedback Buttons + Comment */}
              <HStack spacing={3}>
                <Button
                  size="sm"
                  colorScheme="green"
                  variant="outline"
                  onClick={() => handleFeedback('like')}
                >
                  👍 Like
                </Button>
                <Button
                  size="sm"
                  colorScheme="red"
                  variant="outline"
                  onClick={() => handleFeedback('dislike')}
                >
                  👎 Dislike
                </Button>
                <Input
                  placeholder="Add comment (optional)"
                  value={comment}
                  onChange={(e) => setComment(e.target.value)}
                  size="sm"
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      handleCommentSave();
                    }
                  }}
                  onBlur={handleCommentSave}
                />
              </HStack>

              {/* Version History */}
              <VersionHistory
                versions={section.versions || []}
                onRevert={handleRevert}
              />
            </VStack>
          )}
        </VStack>
      </CardBody>
    </Card>
  );
};
