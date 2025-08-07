<template>
  <div class="container">
    <div class="header">
      <span class="mystic-symbol">☯</span>
      <h1>ANCIENT DIVINATION FINDING SYSTEM</h1>
      <span class="mystic-symbol">🔮</span>
    </div>
    
    <div class="divination-form">
      <div class="form-group">
        <div class="input-group">
          <label>SELECT WISDOM TRADITION</label>
          <select v-model="selectedMethod">
            <option value="">CHOOSE AN ANCIENT SYSTEM</option>
            <option v-for="option in heroOptions" 
                    :key="option.value" 
                    :value="option.value">
              {{ option.label }}
            </option>
          </select>
        </div>
        
        <div class="input-group">
          <label>VISUAL CLUES (OPTIONAL)</label>
          <div class="file-upload">
            <input 
              ref="fileInput"
              type="file" 
              accept="image/*"
              @change="handleImageUpload"
              class="file-input">
            <div class="upload-button" @click.stop>
              <span>{{ uploadButtonText }}</span>
            </div>
          </div>
        </div>

        <div class="preview-container" v-if="previewUrl">
          <img :src="previewUrl" alt="Preview" class="preview-image">
        </div>
      </div>

      <div class="form-group">
        <div class="input-group">
          <label>MISSING OBJECT</label>
          <input v-model="formData.name" type="text" placeholder="E.G. SILVER NECKLACE, BLACK LAPTOP">
        </div>

        <div class="input-group">
          <label>UNIQUE IDENTIFIERS</label>
          <input v-model="formData.attribute" type="text" placeholder="SCRATCHES, ENGRAVINGS, DISTINGUISHING MARKS">
        </div>

        <div class="input-group">
          <label>Owner Details</label>
          <input v-model="formData.owner" type="text" placeholder="Information about the owner...">
        </div>
      </div>
    </div>

    <button 
      @click="submitDivination" 
      :disabled="!isFormValid"
      :class="{ 'button-disabled': !isFormValid }"
    >
      SEEK ANCIENT WISDOM
    </button>
    
    <div class="result" v-html="divinationResult || defaultMessage"></div>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      heroOptions: [],
      selectedMethod: '',
      previewUrl: '',
      formData: {
        name: '',
        attribute: '',
        owner: ''
      },
      divinationResult: '',
      defaultMessage: '<em>THE UNIVERSE RESPONDS TO SINCERE INQUIRY</em>',
      uploadButtonText: 'ADD PHOTOS RELATED TO YOUR LOSS'
    }
  },
  computed: {
    isFormValid() {
      return this.selectedMethod && this.formData.name && this.formData.attribute
    }
  },
  methods: {
    async loadHeroOptions() {
      try {
        const response = await fetch('/api/get-hero-options')
        const data = await response.json()
        this.heroOptions = data.options
      } catch (error) {
        console.error('Failed to load divination methods:', error)
      }
    },

    async handleImageUpload(event) {
      const file = event.target.files[0]
      if (!file) return

      this.uploadButtonText = file.name
      this.previewUrl = URL.createObjectURL(file)

      const formData = new FormData()
      formData.append('image', file)

      try {
        const response = await fetch('/api/analyze-image', {
          method: 'POST',
          body: formData
        })
        const data = await response.json()
        
        if (data?.result?.lost_object) {
          this.formData.name = data.result.lost_object.name || ''
          this.formData.attribute = data.result.lost_object.attributes?.join(', ') || ''
        }
      } catch (error) {
        console.error('Image analysis failed:', error)
      }
    },
    async submitDivination() {
      if (!this.isFormValid) return

      try {
        // 组合用户输入
        const userInput = `Name: ${this.formData.name}\nAttributes: ${this.formData.attribute}\nOwner: ${this.formData.owner}`;
        
        const response = await fetch('/api/ask', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            prompt_id: this.selectedMethod,
            user_input: userInput
          })
        })

        const result = await response.json()
        this.divinationResult = result?.result || '<div>No divination results returned...</div>'
      } catch (error) {
        console.error('Divination failed:', error)
        this.divinationResult = '<div class="error">Divination failed: ' + error.message + '</div>'
      }
    }
  },
  mounted() {
    this.loadHeroOptions()
  }
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&display=swap');

:root {
  --primary-color: #8B0000;
  --secondary-color: #DAA520;
  --background-color: #FDF5E6;
  --text-color: #2F4F4F;
  --border-color: #D2691E;
}

body {
  margin: 0;
  font-family: 'Cinzel', serif;
  background-color: var(--background-color);
  background-image: 
    linear-gradient(rgba(253, 245, 230, 0.97), rgba(253, 245, 230, 0.97)),
    url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23daa520' fill-opacity='0.1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
  color: var(--text-color);
  min-height: 100vh;
  padding: 20px;
  box-sizing: border-box;
}

.container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 2rem;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 15px;
  box-shadow: 0 0 20px rgba(139, 0, 0, 0.1);
  border: 2px solid var(--border-color);
}

.header {
  text-align: center;
  margin-bottom: 2rem;
  color: var(--primary-color);
  border-bottom: 2px solid var(--border-color);
  padding-bottom: 1rem;
}

.divination-form {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-bottom: 2rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

select, input, button {
  padding: 12px;
  border: 2px solid var(--border-color);
  border-radius: 5px;
  font-family: 'Cinzel', serif;
  background: rgba(255, 255, 255, 0.9);
  transition: all 0.3s ease;
  width: 100%;
  box-sizing: border-box;
}

select:focus, input:focus {
  outline: none;
  border-color: var(--secondary-color);
  box-shadow: 0 0 5px var(--secondary-color);
}

button {
  background: var(--primary-color);
  color: white;
  border: none;
  cursor: pointer;
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-top: 1rem;
}

button:hover:not(.button-disabled) {
  background: var(--secondary-color);
  transform: translateY(-2px);
}

.button-disabled {
  background: #cccccc;
  cursor: not-allowed;
}

.preview-container {
  text-align: center;
  margin-bottom: 1rem;
}

.preview-image {
  max-width: 300px;
  max-height: 300px;
  border-radius: 10px;
  box-shadow: 0 0 10px rgba(0,0,0,0.1);
}

.result {
  margin-top: 2rem;
  padding: 2rem;
  border: 2px solid var(--border-color);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.8);
  min-height: 100px;
}

.mystic-symbol {
  font-size: 2rem;
  color: var(--secondary-color);
  margin: 0 0.5rem;
}

.input-group {
  position: relative;
  margin-bottom: 1rem;
}

.input-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--primary-color);
  font-weight: bold;
}

.file-upload {
  position: relative;
  overflow: hidden;
  cursor: pointer;
}

.file-input {
  position: absolute;
  top: 0;
  left: 0;
  opacity: 0;
  cursor: pointer;
  width: 100%;
  height: 100%;
}

.upload-button {
  padding: 12px;
  text-align: center;
  background: rgba(255, 255, 255, 0.9);
  border: 2px solid var(--border-color);
  border-radius: 5px;
  transition: all 0.3s ease;
}

.upload-button:hover {
  background: var(--secondary-color);
  color: white;
}

.error {
  color: var(--primary-color);
  font-weight: bold;
}

@media (max-width: 768px) {
  .divination-form {
    grid-template-columns: 1fr;
  }
  
  .container {
    padding: 1rem;
  }
}
</style>
