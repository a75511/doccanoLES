<template>
  <v-container>
    <v-card>
      <v-card-title>
        {{ $t('perspectives.create') }}
      </v-card-title>
      <v-card-text>
        <v-form ref="form" v-model="valid">
          <v-text-field
            v-model="perspective.name"
            :rules="[rules.required]"
            :label="$t('perspectives.name')"
            outlined
            required
          />

          <v-textarea
            v-model="perspective.description"
            :label="$t('perspectives.description')"
            outlined
            rows="3"
          />

          <v-subheader>{{ $t('perspectives.attributes') }}</v-subheader>
          <v-card outlined>
            <v-card-text>
              <v-row v-for="(attribute, index) in perspective.attributes" :key="index">
                <v-col cols="6">
                  <v-text-field
                    v-model="attribute.name"
                    :rules="[rules.required]"
                    :label="`Attribute ${index + 1} Name`"
                    outlined
                    required
                  />
                </v-col>
                <v-col cols="4">
                  <v-select
                    v-model="attribute.type"
                    :items="attributeTypes"
                    :rules="[rules.required]"
                    :label="`Attribute ${index + 1} Type`"
                    outlined
                    required
                    @change="handleAttributeTypeChange(index)"
                  />
                </v-col>
                <v-col cols="2">
                  <v-btn
                    v-if="perspective.attributes.length > 1"
                    icon
                    color="error"
                    @click="removeAttribute(index)"
                  >
                    <v-icon>{{ mdiMinusCircleOutline }}</v-icon>
                  </v-btn>
                </v-col>

                <v-col v-if="attribute.type === 'List'" cols="12">
                  <v-subheader>Options</v-subheader>
                  <v-row v-for="(option, optIndex) in attribute.options" :key="optIndex">
                    <v-col cols="10">
                      <v-text-field
                        v-model="option.value"
                        :rules="[rules.required]"
                        :label="`Option ${optIndex + 1}`"
                        outlined
                        required
                      />
                    </v-col>
                    <v-col cols="2">
                      <v-btn v-if="attribute.options.length > 1" icon color="error" 
                        @click="removeOption(index, optIndex)">
                        <v-icon>{{ mdiMinusCircleOutline }}</v-icon>
                      </v-btn>
                    </v-col>
                  </v-row>
<v-btn text color="primary" :disabled="attribute.options.length >= 10" @click="addOption(index)">
                    {{ $t('perspectives.add_option') }}
                  </v-btn>
                </v-col>
              </v-row>
            </v-card-text>
            <v-card-actions>
              <v-btn color="primary" text :disabled="perspective.attributes.length >= 15" 
              @click="addAttribute">
                {{ $t('perspectives.add_attribute') }}
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-btn color="primary" :disabled="!valid" :loading="loading" @click="createPerspective">
          {{ $t('generic.create') }}
        </v-btn>
        <v-btn color="grey" @click="$router.back()">
          {{ $t('generic.cancel') }}
        </v-btn>
      </v-card-actions>

      <v-alert v-if="errorMessage" type="error" class="mt-4">
        {{ errorMessage }}
      </v-alert>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import Vue from 'vue';
import { mdiMinusCircleOutline } from '@mdi/js';
import { mapGetters } from 'vuex';

export default Vue.extend({
  layout: 'project',

  data() {
    return {
      valid: false,
      loading: false,
      perspective: {
        name: '',
        description: '',
        attributes: [{ name: '', type: '', options: [] as { value: string }[] }],
      },
      attributeTypes: ['Text', 'Number', 'Boolean', 'List'],
      rules: {
        required: (v: string) => !!v || 'This field is required',
      },
      successMessage: '',
      errorMessage: '',
      mdiMinusCircleOutline,
    };
  },

  computed: {
    ...mapGetters('projects', {
      currentProject: 'currentProject',
    }),

    projectId(): string {
      return this.$route.params.id
    }
  },

  methods: {
    addAttribute() {
      if (this.perspective.attributes.length < 20) {
        this.perspective.attributes.push({ name: '', type: '', options: [] });
      }
    },

    removeAttribute(index: number) {
      if (this.perspective.attributes.length > 1) {
        this.perspective.attributes.splice(index, 1);
      }
    },

    addOption(attributeIndex: number) {
      this.perspective.attributes[attributeIndex].options.push({ value: '' });
    },

    removeOption(attributeIndex: number, optionIndex: number) {
      if (this.perspective.attributes[attributeIndex].options.length > 1) {
        this.perspective.attributes[attributeIndex].options.splice(optionIndex, 1);
      }
    },

    handleAttributeTypeChange(index: number) {
      const attribute = this.perspective.attributes[index];
      if (attribute.type === 'List' && attribute.options.length === 0) {
        this.$set(attribute, 'options', [{ value: '' }]);
      }
    },

     async createPerspective() {

      this.loading = true;
      this.errorMessage = '';
      
      try {
        const formattedAttributes = this.perspective.attributes.map(attr => ({
          name: attr.name,
          type: attr.type.toLocaleLowerCase(),
          options: attr.type === 'List' ? attr.options.map(opt => ({ value: opt.value })) : undefined
        }));

        await this.$services.perspective.create(
          this.projectId,
          this.perspective.name,
          this.perspective.description,
          formattedAttributes
        );

        this.$store.dispatch('message/setMessage', {
          message: 'Perspective created successfully!',
          color: 'success',
        });

        setTimeout(() => {
          this.$router.push(`/projects/${this.projectId}/perspectives`);
        }, 1000);
      } catch (error: any) {
        this.errorMessage = error.message;
      } finally {
        this.loading = false;
      }
    },
  },
});
</script>
