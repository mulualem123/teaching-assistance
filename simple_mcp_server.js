#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ErrorCode,
  ListToolsRequestSchema,
  McpError,
} from '@modelcontextprotocol/sdk/types.js';

class SimpleMcpServer {
  constructor() {
    this.server = new Server(
      {
        name: 'simple-mcp-server',
        version: '0.1.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupToolHandlers();
  }

  setupToolHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: 'hello_world',
          description: 'Returns a greeting',
          inputSchema: {
            type: 'object',
            properties: {
              name: {
                type: 'string',
                description: 'The name to greet',
              },
            },
            required: ['name'],
          },
        },
      ],
    }));

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      if (request.params.name !== 'hello_world') {
        throw new McpError(
          ErrorCode.MethodNotFound,
          `Unknown tool: ${request.params.name}`
        );
      }

      const name = request.params.arguments.name;

      return {
        content: [
          {
            type: 'text',
            text: `Hello, ${name}!`,
          },
        ],
      };
    });
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('Simple MCP server running on stdio');
  }
}

const server = new SimpleMcpServer();
server.run().catch(console.error);
