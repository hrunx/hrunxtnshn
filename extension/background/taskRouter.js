/**
 * Task Router
 * Routes and executes tasks based on action type
 */

const taskRouter = {
  /**
   * Execute a task
   */
  async execute(task) {
    console.log('Executing task:', task);
    
    // Check if we need to use API for planning
    if (task.prompt || task.description || task.needsPlanning) {
      return await this.executeWithPlanning(task);
    }
    
    // Direct action execution
    if (task.action) {
      return await this.executeAction(task);
    }
    
    // Array of actions
    if (task.actions && Array.isArray(task.actions)) {
      const results = [];
      for (const action of task.actions) {
        const result = await this.executeAction(action);
        results.push(result);
      }
      return results;
    }
    
    throw new Error('Invalid task format');
  },

  /**
   * Execute task with AI planning
   */
  async executeWithPlanning(task) {
    console.log('Executing task with AI planning');
    
    // Get plan from API
    const planResult = await apiClient.executeTask(task);
    
    // Execute planned actions
    if (planResult.actions && Array.isArray(planResult.actions)) {
      const results = [];
      for (const action of planResult.actions) {
        const result = await this.executeAction(action);
        results.push(result);
      }
      return {
        plan: planResult.actions,
        results: results,
        raw: planResult.raw
      };
    }
    
    // If no actions, return the plan result
    return planResult;
  },

  /**
   * Execute a single action
   */
  async executeAction(action) {
    const actionType = action.action || action.type;
    
    switch (actionType) {
      case 'LOAD_PAGE':
        return await offscreenController.load(action.url);
      
      case 'FETCH':
        return await fetchEngine.fetchWithSession(action.url);
      
      case 'EXTRACT_MAPS':
        return await extractorRouter.maps(action.url);
      
      case 'EXTRACT_LINKEDIN':
        return await extractorRouter.linkedin(action.url);
      
      case 'EXTRACT_INSTAGRAM':
        return await extractorRouter.instagram(action.url);
      
      case 'WAIT':
        await new Promise(resolve => setTimeout(resolve, action.duration || 1000));
        return { ok: true };
      
      case 'NAVIGATE':
        // Navigate to URL in active tab
        const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
        if (tabs[0]) {
          await chrome.tabs.update(tabs[0].id, { url: action.url });
        }
        return { ok: true };
      
      default:
        throw new Error('Unknown action: ' + actionType);
    }
  }
};
