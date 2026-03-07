<template>
  <div class="row justify-content-center mt-5">
    <div class="col-md-4">
      <div class="card shadow p-4">
        <h3 class="text-center mb-4">PPA Login</h3>
        <div class="mb-3">
          <label>Email</label>
          <input v-model="email" type="email" class="form-control">
        </div>
        <div class="mb-3">
          <label>Password</label>
          <input v-model="password" type="password" class="form-control">
        </div>
        <button @click="login" class="btn btn-primary w-100">Login</button>
        <p class="text-danger mt-2" v-if="error">{{ error }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  data() { return { email: '', password: '', error: '' } },
  methods: {
    async login() {
      try {
        const res = await axios.post('http://localhost:5000/api/login', {
          email: this.email, password: this.password
        })
        localStorage.setItem('token', res.data.token)
        localStorage.setItem('role', res.data.role)
        
        if (res.data.role === 'admin') this.$router.push('/admin')
        else if (res.data.role === 'student') this.$router.push('/student')
        else this.$router.push('/company')
      } catch (err) { this.error = "Invalid Credentials" }
    }
  }
}
</script>